# crm/utils/notification_manager.py
"""
Notification Manager Module für CRM
Implementiert automatische Erinnerungen und Follow-ups mit Regel-Engine

Author: Kiro AI
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import Any, Optional

try:
    from database import get_db_connection
except ImportError:
    def get_db_connection():
        """Fallback wenn database.py nicht verfügbar"""
        return None


# ============================================================================
# Regel-Engine für automatische Erinnerungen
# ============================================================================

# Regel-Definitionen
REMINDER_RULES = {
    'lead_created': {
        'days_offset': 3,
        'message_template': 'Follow-up für Lead: {name}',
        'description': 'Lead erstellt → Follow-up nach 3 Tagen'
    },
    'offer_sent': {
        'days_offset': 7,
        'message_template': 'Follow-up für Angebot: {name}',
        'description': 'Angebot versendet → Follow-up nach 7 Tagen'
    },
    'appointment_completed': {
        'days_offset': 1,
        'message_template': 'Follow-up nach Termin: {name}',
        'description': 'Termin → Follow-up nach 1 Tag'
    }
}


def create_reminder(
    reminder_type: str,
    related_id: int,
    related_type: str,
    due_date: Optional[date] = None,
    message: Optional[str] = None,
    auto_calculate_date: bool = True
) -> Optional[int]:
    """
    Erstellt eine neue Erinnerung.
    
    Args:
        reminder_type: Typ der Erinnerung (lead_created, offer_sent, appointment_completed, manual)
        related_id: ID des verknüpften Objekts (Lead, Projekt, Termin)
        related_type: Typ des verknüpften Objekts (lead, project, appointment, customer)
        due_date: Fälligkeitsdatum (optional, wird automatisch berechnet wenn auto_calculate_date=True)
        message: Nachricht der Erinnerung
        auto_calculate_date: Ob das Datum automatisch basierend auf Regeln berechnet werden soll
    
    Returns:
        Reminder-ID bei Erfolg, None bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        print("Notification Manager: Keine Datenbankverbindung")
        return None
    
    try:
        cursor = conn.cursor()
        
        # Berechne Fälligkeitsdatum basierend auf Regel
        if auto_calculate_date and reminder_type in REMINDER_RULES:
            rule = REMINDER_RULES[reminder_type]
            days_offset = rule['days_offset']
            calculated_due_date = date.today() + timedelta(days=days_offset)
            
            if due_date is None:
                due_date = calculated_due_date
            
            # Generiere Nachricht aus Template wenn keine angegeben
            if message is None:
                message = rule['message_template'].format(name=f"{related_type} #{related_id}")
        
        # Validierung
        if due_date is None:
            print("Notification Manager: Fälligkeitsdatum ist erforderlich")
            return None
        
        # Erinnerung erstellen
        cursor.execute("""
            INSERT INTO crm_reminders (
                reminder_type, related_id, related_type, due_date, 
                status, message, repeat_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            reminder_type,
            related_id,
            related_type,
            due_date.isoformat() if isinstance(due_date, date) else due_date,
            'pending',
            message or f"Erinnerung für {related_type} #{related_id}",
            0
        ))
        
        conn.commit()
        reminder_id = cursor.lastrowid
        
        print(f"Notification Manager: Erinnerung #{reminder_id} erstellt für {related_type} #{related_id}")
        return reminder_id
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Erstellen: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_reminder(reminder_id: int) -> Optional[dict[str, Any]]:
    """
    Lädt eine einzelne Erinnerung.
    
    Args:
        reminder_id: ID der Erinnerung
    
    Returns:
        Reminder-Dictionary oder None
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crm_reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Laden: {e}")
        return None
    finally:
        conn.close()


def update_reminder_status(
    reminder_id: int,
    new_status: str
) -> bool:
    """
    Aktualisiert den Status einer Erinnerung.
    
    Args:
        reminder_id: ID der Erinnerung
        new_status: Neuer Status (pending, completed, snoozed, dismissed)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Validierung
        valid_statuses = ['pending', 'completed', 'snoozed', 'dismissed']
        if new_status not in valid_statuses:
            print(f"Notification Manager: Ungültiger Status '{new_status}'")
            return False
        
        cursor.execute("""
            UPDATE crm_reminders 
            SET status = ? 
            WHERE id = ?
        """, (new_status, reminder_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Notification Manager: Erinnerung #{reminder_id} Status auf '{new_status}' gesetzt")
            return True
        else:
            print(f"Notification Manager: Erinnerung #{reminder_id} nicht gefunden")
            return False
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Aktualisieren: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def snooze_reminder(reminder_id: int, days: int = 2) -> bool:
    """
    Verschiebt eine Erinnerung um X Tage (Snooze-Funktion).
    
    Args:
        reminder_id: ID der Erinnerung
        days: Anzahl Tage zum Verschieben (Standard: 2)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Lade aktuelle Erinnerung
        cursor.execute("SELECT due_date, repeat_count FROM crm_reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Notification Manager: Erinnerung #{reminder_id} nicht gefunden")
            return False
        
        current_due_date_str = row[0]
        repeat_count = row[1] or 0
        
        # Parse aktuelles Datum
        try:
            current_due_date = datetime.fromisoformat(current_due_date_str).date()
        except (ValueError, AttributeError):
            current_due_date = date.today()
        
        # Berechne neues Datum
        new_due_date = current_due_date + timedelta(days=days)
        
        # Update Erinnerung
        cursor.execute("""
            UPDATE crm_reminders 
            SET due_date = ?, status = 'snoozed', repeat_count = ?
            WHERE id = ?
        """, (new_due_date.isoformat(), repeat_count + 1, reminder_id))
        
        conn.commit()
        
        print(f"Notification Manager: Erinnerung #{reminder_id} um {days} Tage verschoben auf {new_due_date}")
        return True
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Snoozen: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_reminder(reminder_id: int) -> bool:
    """
    Löscht eine Erinnerung.
    
    Args:
        reminder_id: ID der Erinnerung
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crm_reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Notification Manager: Erinnerung #{reminder_id} gelöscht")
            return True
        else:
            print(f"Notification Manager: Erinnerung #{reminder_id} nicht gefunden")
            return False
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Löschen: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ============================================================================
# Abfrage-Funktionen
# ============================================================================

def get_all_reminders(
    status: Optional[str] = None,
    related_type: Optional[str] = None,
    related_id: Optional[int] = None,
    due_only: bool = False
) -> list[dict[str, Any]]:
    """
    Lädt alle Erinnerungen mit optionaler Filterung.
    
    Args:
        status: Filter nach Status
        related_type: Filter nach verknüpftem Typ
        related_id: Filter nach verknüpfter ID
        due_only: Nur fällige Erinnerungen
    
    Returns:
        Liste von Reminder-Dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Baue WHERE-Klausel dynamisch
        where_clauses = []
        values = []
        
        if status:
            where_clauses.append("status = ?")
            values.append(status)
        
        if related_type:
            where_clauses.append("related_type = ?")
            values.append(related_type)
        
        if related_id:
            where_clauses.append("related_id = ?")
            values.append(related_id)
        
        if due_only:
            today = date.today().isoformat()
            where_clauses.append("due_date <= ?")
            values.append(today)
            where_clauses.append("status IN ('pending', 'snoozed')")
        
        # Baue SQL-Query
        sql = "SELECT * FROM crm_reminders"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY due_date ASC, created_at DESC"
        
        cursor.execute(sql, values)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Laden aller Erinnerungen: {e}")
        return []
    finally:
        conn.close()


def get_due_reminders() -> list[dict[str, Any]]:
    """
    Lädt alle fälligen Erinnerungen (heute oder überfällig).
    
    Returns:
        Liste von fälligen Erinnerungen
    """
    return get_all_reminders(due_only=True)


def get_reminders_by_type(reminder_type: str) -> list[dict[str, Any]]:
    """Lädt alle Erinnerungen eines bestimmten Typs."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM crm_reminders 
            WHERE reminder_type = ?
            ORDER BY due_date ASC
        """, (reminder_type,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Laden nach Typ: {e}")
        return []
    finally:
        conn.close()


def get_reminders_for_related_object(
    related_type: str,
    related_id: int
) -> list[dict[str, Any]]:
    """
    Lädt alle Erinnerungen für ein bestimmtes Objekt.
    
    Args:
        related_type: Typ des Objekts (lead, project, appointment, customer)
        related_id: ID des Objekts
    
    Returns:
        Liste von Erinnerungen
    """
    return get_all_reminders(related_type=related_type, related_id=related_id)


# ============================================================================
# Automatische Erinnerungs-Erstellung (Regel-Engine)
# ============================================================================

def create_reminder_for_lead(lead_id: int, lead_name: str = "") -> Optional[int]:
    """
    Erstellt automatische Erinnerung für neuen Lead (Follow-up nach 3 Tagen).
    
    Args:
        lead_id: ID des Leads
        lead_name: Name des Leads (optional)
    
    Returns:
        Reminder-ID bei Erfolg, None bei Fehler
    """
    message = f"Follow-up für Lead: {lead_name or f'#{lead_id}'}"
    return create_reminder(
        reminder_type='lead_created',
        related_id=lead_id,
        related_type='lead',
        message=message,
        auto_calculate_date=True
    )


def create_reminder_for_offer(project_id: int, project_name: str = "") -> Optional[int]:
    """
    Erstellt automatische Erinnerung für versendetes Angebot (Follow-up nach 7 Tagen).
    
    Args:
        project_id: ID des Projekts
        project_name: Name des Projekts (optional)
    
    Returns:
        Reminder-ID bei Erfolg, None bei Fehler
    """
    message = f"Follow-up für Angebot: {project_name or f'Projekt #{project_id}'}"
    return create_reminder(
        reminder_type='offer_sent',
        related_id=project_id,
        related_type='project',
        message=message,
        auto_calculate_date=True
    )


def create_reminder_for_appointment(appointment_id: int, appointment_title: str = "") -> Optional[int]:
    """
    Erstellt automatische Erinnerung nach Termin (Follow-up nach 1 Tag).
    
    Args:
        appointment_id: ID des Termins
        appointment_title: Titel des Termins (optional)
    
    Returns:
        Reminder-ID bei Erfolg, None bei Fehler
    """
    message = f"Follow-up nach Termin: {appointment_title or f'#{appointment_id}'}"
    return create_reminder(
        reminder_type='appointment_completed',
        related_id=appointment_id,
        related_type='appointment',
        message=message,
        auto_calculate_date=True
    )


def create_manual_reminder(
    related_id: int,
    related_type: str,
    due_date: date,
    message: str
) -> Optional[int]:
    """
    Erstellt eine manuelle Erinnerung.
    
    Args:
        related_id: ID des verknüpften Objekts
        related_type: Typ des verknüpften Objekts
        due_date: Fälligkeitsdatum
        message: Nachricht
    
    Returns:
        Reminder-ID bei Erfolg, None bei Fehler
    """
    return create_reminder(
        reminder_type='manual',
        related_id=related_id,
        related_type=related_type,
        due_date=due_date,
        message=message,
        auto_calculate_date=False
    )


# ============================================================================
# Statistik-Funktionen
# ============================================================================

def get_reminder_statistics() -> dict[str, Any]:
    """
    Liefert Statistiken über alle Erinnerungen.
    
    Returns:
        Dictionary mit Statistiken
    """
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        
        stats = {}
        
        # Gesamt-Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM crm_reminders")
        stats['total'] = cursor.fetchone()['count']
        
        # Nach Status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM crm_reminders 
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Fällige Erinnerungen
        today = date.today().isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM crm_reminders 
            WHERE due_date <= ? AND status IN ('pending', 'snoozed')
        """, (today,))
        stats['due'] = cursor.fetchone()['count']
        
        # Heute fällig
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM crm_reminders 
            WHERE due_date = ? AND status IN ('pending', 'snoozed')
        """, (today,))
        stats['due_today'] = cursor.fetchone()['count']
        
        # Nach Typ
        cursor.execute("""
            SELECT reminder_type, COUNT(*) as count 
            FROM crm_reminders 
            WHERE status IN ('pending', 'snoozed')
            GROUP BY reminder_type
        """)
        stats['by_type'] = {row['reminder_type']: row['count'] for row in cursor.fetchall()}
        
        # Durchschnittliche Snooze-Anzahl
        cursor.execute("""
            SELECT AVG(repeat_count) as avg_snooze 
            FROM crm_reminders 
            WHERE repeat_count > 0
        """)
        avg_snooze = cursor.fetchone()['avg_snooze']
        stats['avg_snooze_count'] = round(avg_snooze, 1) if avg_snooze else 0
        
        return stats
        
    except Exception as e:
        print(f"Notification Manager Fehler beim Laden der Statistiken: {e}")
        return {}
    finally:
        conn.close()


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def is_reminder_overdue(reminder: dict[str, Any]) -> bool:
    """Prüft ob eine Erinnerung überfällig ist."""
    if reminder.get('status') in ['completed', 'dismissed']:
        return False
    
    due_date_str = reminder.get('due_date')
    if not due_date_str:
        return False
    
    try:
        due_date = datetime.fromisoformat(due_date_str).date()
        return due_date < date.today()
    except (ValueError, AttributeError):
        return False


def get_reminder_display_color(reminder: dict[str, Any]) -> str:
    """
    Liefert eine Farbe für die Reminder-Anzeige basierend auf Status und Fälligkeit.
    
    Returns:
        Hex-Farbcode
    """
    status = reminder.get('status', 'pending')
    
    if status == 'completed':
        return '#22C55E'  # Grün
    elif status == 'dismissed':
        return '#64748B'  # Grau
    
    if is_reminder_overdue(reminder):
        return '#EF4444'  # Rot
    
    # Prüfe ob heute fällig
    due_date_str = reminder.get('due_date')
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str).date()
            if due_date == date.today():
                return '#F59E0B'  # Orange
        except (ValueError, AttributeError):
            pass
    
    return '#2563EB'  # Blau


def format_reminder_for_display(reminder: dict[str, Any]) -> dict[str, Any]:
    """
    Formatiert eine Erinnerung für die Anzeige mit zusätzlichen Informationen.
    
    Returns:
        Erweitertes Reminder-Dictionary
    """
    display_reminder = reminder.copy()
    
    # Füge Display-Informationen hinzu
    display_reminder['is_overdue'] = is_reminder_overdue(reminder)
    display_reminder['display_color'] = get_reminder_display_color(reminder)
    
    # Status-Labels
    status_labels = {
        'pending': '⏳ Ausstehend',
        'completed': 'Erledigt',
        'snoozed': ' Verschoben',
        'dismissed': 'Verworfen'
    }
    display_reminder['status_label'] = status_labels.get(reminder.get('status', 'pending'), 'Unbekannt')
    
    # Typ-Labels
    type_labels = {
        'lead_created': ' Lead Follow-up',
        'offer_sent': ' Angebots Follow-up',
        'appointment_completed': ' Termin Follow-up',
        'manual': ' Manuelle Erinnerung'
    }
    display_reminder['type_label'] = type_labels.get(reminder.get('reminder_type', 'manual'), 'Erinnerung')
    
    # Formatiere Datum
    due_date_str = reminder.get('due_date')
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str).date()
            today = date.today()
            
            if due_date == today:
                display_reminder['due_date_label'] = '⏰ Heute'
            elif due_date == today + timedelta(days=1):
                display_reminder['due_date_label'] = ' Morgen'
            elif due_date < today:
                days_overdue = (today - due_date).days
                display_reminder['due_date_label'] = f'{days_overdue} Tag(e) überfällig'
            else:
                days_until = (due_date - today).days
                display_reminder['due_date_label'] = f' In {days_until} Tag(en)'
        except (ValueError, AttributeError):
            display_reminder['due_date_label'] = due_date_str
    else:
        display_reminder['due_date_label'] = 'Kein Datum'
    
    return display_reminder


# ============================================================================
# Export-Funktion für Modul-Test
# ============================================================================

if __name__ == "__main__":
    print("Notification Manager Module - Test")
    print("=" * 50)
    
    # Test: Statistiken laden
    stats = get_reminder_statistics()
    print(f"\nErinnerungs-Statistiken:")
    print(f"  Gesamt: {stats.get('total', 0)}")
    print(f"  Fällig: {stats.get('due', 0)}")
    print(f"  Heute fällig: {stats.get('due_today', 0)}")
    print(f"  Durchschnittliche Snooze-Anzahl: {stats.get('avg_snooze_count', 0)}")
    
    # Test: Fällige Erinnerungen
    due_reminders = get_due_reminders()
    print(f"\nFällige Erinnerungen: {len(due_reminders)}")
    
    print("\n" + "=" * 50)
    print("Notification Manager Module erfolgreich geladen!")
