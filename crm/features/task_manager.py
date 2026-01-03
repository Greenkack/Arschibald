# crm/features/task_manager.py
"""
Task Management Module für CRM
Implementiert vollständige Aufgabenverwaltung mit CRUD-Operationen,
Status-Workflow, Prioritäten und Benachrichtigungen.

Author: Kiro AI
Version: 1.0
Date: 2025-01-13
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
# CRUD-Funktionen für Tasks
# ============================================================================

def create_task(
    title: str,
    description: str = "",
    status: str = "open",
    priority: str = "medium",
    due_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    assigned_to: str = ""
) -> Optional[int]:
    """
    Erstellt eine neue Aufgabe.
    
    Args:
        title: Titel der Aufgabe (erforderlich)
        description: Beschreibung der Aufgabe
        status: Status ('open', 'in_progress', 'completed')
        priority: Priorität ('low', 'medium', 'high')
        due_date: Fälligkeitsdatum
        customer_id: Zuordnung zu Kunde
        project_id: Zuordnung zu Projekt
        lead_id: Zuordnung zu Lead
        assigned_to: Zugewiesener Benutzer
    
    Returns:
        Task-ID bei Erfolg, None bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        print("Task Manager: Keine Datenbankverbindung")
        return None
    
    try:
        cursor = conn.cursor()
        
        # Validierung
        if not title or not title.strip():
            print("Task Manager: Titel ist erforderlich")
            return None
        
        if status not in ['open', 'in_progress', 'completed']:
            print(f"Task Manager: Ungültiger Status '{status}', verwende 'open'")
            status = 'open'
        
        if priority not in ['low', 'medium', 'high']:
            print(f"Task Manager: Ungültige Priorität '{priority}', verwende 'medium'")
            priority = 'medium'
        
        # Task erstellen
        cursor.execute("""
            INSERT INTO crm_tasks (
                title, description, status, priority, due_date,
                customer_id, project_id, lead_id, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title.strip(),
            description.strip() if description else "",
            status,
            priority,
            due_date.isoformat() if due_date else None,
            customer_id,
            project_id,
            lead_id,
            assigned_to.strip() if assigned_to else ""
        ))
        
        conn.commit()
        task_id = cursor.lastrowid
        
        print(f"Task Manager: Task #{task_id} erstellt: '{title}'")
        return task_id
        
    except Exception as e:
        print(f"Task Manager Fehler beim Erstellen: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_task(task_id: int) -> Optional[dict[str, Any]]:
    """
    Lädt eine einzelne Aufgabe.
    
    Args:
        task_id: ID der Aufgabe
    
    Returns:
        Task-Dictionary oder None
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crm_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        print(f"Task Manager Fehler beim Laden: {e}")
        return None
    finally:
        conn.close()


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    assigned_to: Optional[str] = None
) -> bool:
    """
    Aktualisiert eine Aufgabe.
    Nur übergebene Parameter werden aktualisiert.
    
    Args:
        task_id: ID der Aufgabe
        title: Neuer Titel
        description: Neue Beschreibung
        status: Neuer Status
        priority: Neue Priorität
        due_date: Neues Fälligkeitsdatum
        customer_id: Neue Kundenzuordnung
        project_id: Neue Projektzuordnung
        lead_id: Neue Lead-Zuordnung
        assigned_to: Neuer Zugewiesener
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Prüfe ob Task existiert
        cursor.execute("SELECT id FROM crm_tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            print(f"Task Manager: Task #{task_id} nicht gefunden")
            return False
        
        # Baue UPDATE-Statement dynamisch
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = ?")
            values.append(title.strip())
        
        if description is not None:
            updates.append("description = ?")
            values.append(description.strip())
        
        if status is not None:
            if status not in ['open', 'in_progress', 'completed']:
                print(f"Task Manager: Ungültiger Status '{status}'")
                return False
            updates.append("status = ?")
            values.append(status)
            
            # Wenn Status auf 'completed' gesetzt wird, setze completed_at
            if status == 'completed':
                updates.append("completed_at = ?")
                values.append(datetime.now().isoformat())
        
        if priority is not None:
            if priority not in ['low', 'medium', 'high']:
                print(f"Task Manager: Ungültige Priorität '{priority}'")
                return False
            updates.append("priority = ?")
            values.append(priority)
        
        if due_date is not None:
            updates.append("due_date = ?")
            values.append(due_date.isoformat() if due_date else None)
        
        if customer_id is not None:
            updates.append("customer_id = ?")
            values.append(customer_id)
        
        if project_id is not None:
            updates.append("project_id = ?")
            values.append(project_id)
        
        if lead_id is not None:
            updates.append("lead_id = ?")
            values.append(lead_id)
        
        if assigned_to is not None:
            updates.append("assigned_to = ?")
            values.append(assigned_to.strip())
        
        if not updates:
            print("Task Manager: Keine Änderungen zum Aktualisieren")
            return True
        
        # Führe UPDATE aus
        values.append(task_id)
        sql = f"UPDATE crm_tasks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        
        print(f"Task Manager: Task #{task_id} aktualisiert")
        return True
        
    except Exception as e:
        print(f"Task Manager Fehler beim Aktualisieren: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_task(task_id: int) -> bool:
    """
    Löscht eine Aufgabe.
    
    Args:
        task_id: ID der Aufgabe
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM crm_tasks WHERE id = ?", (task_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Task Manager: Task #{task_id} gelöscht")
            return True
        else:
            print(f"Task Manager: Task #{task_id} nicht gefunden")
            return False
        
    except Exception as e:
        print(f"Task Manager Fehler beim Löschen: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ============================================================================
# Abfrage-Funktionen mit Filterung
# ============================================================================

def get_all_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    assigned_to: Optional[str] = None,
    overdue_only: bool = False,
    due_soon_days: Optional[int] = None
) -> list[dict[str, Any]]:
    """
    Lädt alle Aufgaben mit optionaler Filterung.
    
    Args:
        status: Filter nach Status
        priority: Filter nach Priorität
        customer_id: Filter nach Kunde
        project_id: Filter nach Projekt
        lead_id: Filter nach Lead
        assigned_to: Filter nach Zugewiesenem
        overdue_only: Nur überfällige Tasks
        due_soon_days: Tasks die in X Tagen fällig sind
    
    Returns:
        Liste von Task-Dictionaries
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
        
        if priority:
            where_clauses.append("priority = ?")
            values.append(priority)
        
        if customer_id:
            where_clauses.append("customer_id = ?")
            values.append(customer_id)
        
        if project_id:
            where_clauses.append("project_id = ?")
            values.append(project_id)
        
        if lead_id:
            where_clauses.append("lead_id = ?")
            values.append(lead_id)
        
        if assigned_to:
            where_clauses.append("assigned_to = ?")
            values.append(assigned_to)
        
        if overdue_only:
            today = date.today().isoformat()
            where_clauses.append("due_date < ? AND status != 'completed'")
            values.append(today)
        
        if due_soon_days is not None:
            today = date.today()
            future_date = (today + timedelta(days=due_soon_days)).isoformat()
            where_clauses.append("due_date <= ? AND due_date >= ? AND status != 'completed'")
            values.append(future_date)
            values.append(today.isoformat())
        
        # Baue SQL-Query
        sql = "SELECT * FROM crm_tasks"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY due_date ASC, priority DESC, created_at DESC"
        
        cursor.execute(sql, values)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"Task Manager Fehler beim Laden aller Tasks: {e}")
        return []
    finally:
        conn.close()


def get_tasks_by_customer(customer_id: int) -> list[dict[str, Any]]:
    """Lädt alle Tasks für einen Kunden."""
    return get_all_tasks(customer_id=customer_id)


def get_tasks_by_project(project_id: int) -> list[dict[str, Any]]:
    """Lädt alle Tasks für ein Projekt."""
    return get_all_tasks(project_id=project_id)


def get_tasks_by_lead(lead_id: int) -> list[dict[str, Any]]:
    """Lädt alle Tasks für einen Lead."""
    return get_all_tasks(lead_id=lead_id)


def get_overdue_tasks() -> list[dict[str, Any]]:
    """Lädt alle überfälligen Tasks."""
    return get_all_tasks(overdue_only=True)


def get_tasks_due_soon(days: int = 7) -> list[dict[str, Any]]:
    """Lädt alle Tasks die in den nächsten X Tagen fällig sind."""
    return get_all_tasks(due_soon_days=days)


# ============================================================================
# Status-Workflow-Funktionen
# ============================================================================

def mark_task_in_progress(task_id: int) -> bool:
    """Setzt Task-Status auf 'in_progress'."""
    return update_task(task_id, status='in_progress')


def mark_task_completed(task_id: int) -> bool:
    """Setzt Task-Status auf 'completed' und setzt completed_at."""
    return update_task(task_id, status='completed')


def reopen_task(task_id: int) -> bool:
    """Setzt Task-Status zurück auf 'open'."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE crm_tasks 
            SET status = 'open', completed_at = NULL 
            WHERE id = ?
        """, (task_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Task Manager: Task #{task_id} wieder geöffnet")
            return True
        return False
        
    except Exception as e:
        print(f"Task Manager Fehler beim Wiedereröffnen: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ============================================================================
# Statistik-Funktionen
# ============================================================================

def get_task_statistics() -> dict[str, Any]:
    """
    Liefert Statistiken über alle Tasks.
    
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
        cursor.execute("SELECT COUNT(*) as count FROM crm_tasks")
        stats['total'] = cursor.fetchone()['count']
        
        # Nach Status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM crm_tasks 
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Nach Priorität
        cursor.execute("""
            SELECT priority, COUNT(*) as count 
            FROM crm_tasks 
            WHERE status != 'completed'
            GROUP BY priority
        """)
        stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        # Überfällige Tasks
        today = date.today().isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM crm_tasks 
            WHERE due_date < ? AND status != 'completed'
        """, (today))
        stats['overdue'] = cursor.fetchone()['count']
        
        # Heute fällig
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM crm_tasks 
            WHERE due_date = ? AND status != 'completed'
        """, (today))
        stats['due_today'] = cursor.fetchone()['count']
        
        # Diese Woche fällig
        week_end = (date.today() + timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM crm_tasks 
            WHERE due_date BETWEEN ? AND ? AND status != 'completed'
        """, (today, week_end))
        stats['due_this_week'] = cursor.fetchone()['count']
        
        return stats
        
    except Exception as e:
        print(f"Task Manager Fehler beim Laden der Statistiken: {e}")
        return {}
    finally:
        conn.close()


# ============================================================================
# Benachrichtigungs-Funktionen
# ============================================================================

def get_tasks_needing_notification() -> list[dict[str, Any]]:
    """
    Liefert alle Tasks die eine Benachrichtigung benötigen:
    - Überfällige Tasks
    - Heute fällige Tasks
    - Morgen fällige Tasks
    
    Returns:
        Liste von Tasks mit Benachrichtigungstyp
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        today = date.today()
        tomorrow = (today + timedelta(days=1)).isoformat()
        today_str = today.isoformat()
        
        notifications = []
        
        # Überfällige Tasks
        cursor.execute("""
            SELECT * FROM crm_tasks 
            WHERE due_date < ? AND status != 'completed'
            ORDER BY due_date ASC
        """, (today_str))
        
        for row in cursor.fetchall():
            task = dict(row)
            task['notification_type'] = 'overdue'
            task['notification_priority'] = 'high'
            notifications.append(task)
        
        # Heute fällige Tasks
        cursor.execute("""
            SELECT * FROM crm_tasks 
            WHERE due_date = ? AND status != 'completed'
            ORDER BY priority DESC
        """, (today_str))
        
        for row in cursor.fetchall():
            task = dict(row)
            task['notification_type'] = 'due_today'
            task['notification_priority'] = 'medium'
            notifications.append(task)
        
        # Morgen fällige Tasks
        cursor.execute("""
            SELECT * FROM crm_tasks 
            WHERE due_date = ? AND status != 'completed'
            ORDER BY priority DESC
        """, (tomorrow))
        
        for row in cursor.fetchall():
            task = dict(row)
            task['notification_type'] = 'due_tomorrow'
            task['notification_priority'] = 'low'
            notifications.append(task)
        
        return notifications
        
    except Exception as e:
        print(f"Task Manager Fehler beim Laden der Benachrichtigungen: {e}")
        return []
    finally:
        conn.close()


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def is_task_overdue(task: dict[str, Any]) -> bool:
    """Prüft ob ein Task überfällig ist."""
    if task.get('status') == 'completed':
        return False
    
    due_date_str = task.get('due_date')
    if not due_date_str:
        return False
    
    try:
        due_date = datetime.fromisoformat(due_date_str).date()
        return due_date < date.today()
    except (ValueError, AttributeError):
        return False


def get_task_display_color(task: dict[str, Any]) -> str:
    """
    Liefert eine Farbe für die Task-Anzeige basierend auf Status und Fälligkeit.
    
    Returns:
        Hex-Farbcode
    """
    if task.get('status') == 'completed':
        return '#22C55E'  # Grün
    
    if is_task_overdue(task):
        return '#EF4444'  # Rot
    
    priority = task.get('priority', 'medium')
    if priority == 'high':
        return '#F59E0B'  # Orange
    elif priority == 'low':
        return '#64748B'  # Grau
    else:
        return '#2563EB'  # Blau


def format_task_for_display(task: dict[str, Any]) -> dict[str, Any]:
    """
    Formatiert einen Task für die Anzeige mit zusätzlichen Informationen.
    
    Returns:
        Erweitertes Task-Dictionary
    """
    display_task = task.copy()
    
    # Füge Display-Informationen hinzu
    display_task['is_overdue'] = is_task_overdue(task)
    display_task['display_color'] = get_task_display_color(task)
    
    # Status-Labels
    status_labels = {
        'open': ' Offen',
        'in_progress': ' In Arbeit',
        'completed': 'Erledigt'
    }
    display_task['status_label'] = status_labels.get(task.get('status', 'open'), 'Unbekannt')
    
    # Prioritäts-Labels
    priority_labels = {
        'low': ' Niedrig',
        'medium': '🟡 Mittel',
        'high': ' Hoch'
    }
    display_task['priority_label'] = priority_labels.get(task.get('priority', 'medium'), 'Unbekannt')
    
    # Formatiere Datum
    due_date_str = task.get('due_date')
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str).date()
            today = date.today()
            
            if due_date == today:
                display_task['due_date_label'] = '⏰ Heute'
            elif due_date == today + timedelta(days=1):
                display_task['due_date_label'] = ' Morgen'
            elif due_date < today:
                days_overdue = (today - due_date).days
                display_task['due_date_label'] = f'{days_overdue} Tag(e) überfällig'
            else:
                days_until = (due_date - today).days
                display_task['due_date_label'] = f' In {days_until} Tag(en)'
        except (ValueError, AttributeError):
            display_task['due_date_label'] = due_date_str
    else:
        display_task['due_date_label'] = 'Kein Datum'
    
    return display_task


# ============================================================================
# Export-Funktion für Modul-Test
# ============================================================================

if __name__ == "__main__":
    print("Task Manager Module - Test")
    print("=" * 50)
    
    # Test: Statistiken laden
    stats = get_task_statistics()
    print(f"\nTask-Statistiken:")
    print(f"  Gesamt: {stats.get('total', 0)}")
    print(f"  Überfällig: {stats.get('overdue', 0)}")
    print(f"  Heute fällig: {stats.get('due_today', 0)}")
    print(f"  Diese Woche fällig: {stats.get('due_this_week', 0)}")
    
    # Test: Benachrichtigungen
    notifications = get_tasks_needing_notification()
    print(f"\nBenachrichtigungen: {len(notifications)}")
    
    print("\n" + "=" * 50)
    print("Task Manager Module erfolgreich geladen!")
