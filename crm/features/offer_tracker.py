# crm/features/offer_tracker.py
"""
Angebotsverfolgung (Offer Tracking) Modul
Verwaltet den Status und Workflow von Angeboten
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Any


def create_offer_tracking_tables(conn: sqlite3.Connection) -> None:
    """Erstellt/erweitert die Tabellen für Angebotsverfolgung."""
    cursor = conn.cursor()
    
    # Erweitere projects Tabelle um Angebots-Felder
    # Prüfe welche Spalten bereits existieren
    cursor.execute("PRAGMA table_info(projects)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    offer_columns = {
        'offer_status': 'TEXT DEFAULT "draft"',  # draft, sent, accepted, rejected
        'offer_sent_date': 'TEXT',
        'offer_accepted_date': 'TEXT',
        'offer_rejected_date': 'TEXT',
        'offer_version': 'INTEGER DEFAULT 1',
        'offer_value': 'REAL',
        'rejection_reason': 'TEXT',
        'rejection_notes': 'TEXT',
        'follow_up_date': 'TEXT',
        'follow_up_completed': 'INTEGER DEFAULT 0'
    }
    
    for col_name, col_type in offer_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
                print(f"Offer Tracker: Spalte '{col_name}' zur Tabelle 'projects' hinzugefügt.")
            except sqlite3.OperationalError as e:
                print(f"Offer Tracker: Spalte '{col_name}' existiert bereits oder Fehler: {e}")
    
    conn.commit()


def update_offer_status(
    conn: sqlite3.Connection,
    project_id: int,
    new_status: str,
    **kwargs: Any
) -> bool:
    """
    Aktualisiert den Angebotsstatus eines Projekts.
    
    Args:
        conn: Datenbankverbindung
        project_id: ID des Projekts
        new_status: Neuer Status (draft, sent, accepted, rejected)
        **kwargs: Zusätzliche Felder (rejection_reason, offer_value, etc.)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # Basis-Update
        update_fields = ['offer_status = ?', 'last_updated = ?']
        values = [new_status, now]
        
        # Status-spezifische Felder
        if new_status == 'sent':
            update_fields.append('offer_sent_date = ?')
            values.append(kwargs.get('offer_sent_date', now))
            
            # Automatische Follow-up-Erinnerung nach 7 Tagen
            follow_up_date = (datetime.now() + timedelta(days=7)).isoformat()
            update_fields.append('follow_up_date = ?')
            values.append(follow_up_date)
            update_fields.append('follow_up_completed = ?')
            values.append(0)
            
        elif new_status == 'accepted':
            update_fields.append('offer_accepted_date = ?')
            values.append(kwargs.get('offer_accepted_date', now))
            
        elif new_status == 'rejected':
            update_fields.append('offer_rejected_date = ?')
            values.append(kwargs.get('offer_rejected_date', now))
            
            if 'rejection_reason' in kwargs:
                update_fields.append('rejection_reason = ?')
                values.append(kwargs['rejection_reason'])
            
            if 'rejection_notes' in kwargs:
                update_fields.append('rejection_notes = ?')
                values.append(kwargs['rejection_notes'])
        
        # Zusätzliche optionale Felder
        if 'offer_value' in kwargs:
            update_fields.append('offer_value = ?')
            values.append(kwargs['offer_value'])
        
        if 'offer_version' in kwargs:
            update_fields.append('offer_version = ?')
            values.append(kwargs['offer_version'])
        
        # SQL ausführen
        values.append(project_id)
        sql = f"UPDATE projects SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Angebotsstatus: {e}")
        return False


def get_offer_status(conn: sqlite3.Connection, project_id: int) -> dict[str, Any] | None:
    """
    Lädt den Angebotsstatus eines Projekts.
    
    Args:
        conn: Datenbankverbindung
        project_id: ID des Projekts
    
    Returns:
        Dictionary mit Angebotsdaten oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, project_name, offer_status, offer_sent_date,
                offer_accepted_date, offer_rejected_date, offer_version,
                offer_value, rejection_reason, rejection_notes,
                follow_up_date, follow_up_completed, customer_id
            FROM projects
            WHERE id = ?
        """, (project_id))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'id': row[0],
            'project_name': row[1],
            'offer_status': row[2] or 'draft',
            'offer_sent_date': row[3],
            'offer_accepted_date': row[4],
            'offer_rejected_date': row[5],
            'offer_version': row[6] or 1,
            'offer_value': row[7],
            'rejection_reason': row[8],
            'rejection_notes': row[9],
            'follow_up_date': row[10],
            'follow_up_completed': row[11] or 0,
            'customer_id': row[12]
        }
        
    except Exception as e:
        print(f"Fehler beim Laden des Angebotsstatus: {e}")
        return None


def get_all_offers(
    conn: sqlite3.Connection,
    status_filter: str | None = None,
    include_customer_info: bool = True
) -> list[dict[str, Any]]:
    """
    Lädt alle Angebote mit optionalem Statusfilter.
    
    Args:
        conn: Datenbankverbindung
        status_filter: Optional - filtert nach Status (draft, sent, accepted, rejected)
        include_customer_info: Ob Kundeninformationen inkludiert werden sollen
    
    Returns:
        Liste von Angebots-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        if include_customer_info:
            sql = """
                SELECT 
                    p.id, p.project_name, p.offer_status, p.offer_sent_date,
                    p.offer_accepted_date, p.offer_rejected_date, p.offer_version,
                    p.offer_value, p.rejection_reason, p.rejection_notes,
                    p.follow_up_date, p.follow_up_completed, p.customer_id,
                    c.first_name, c.last_name, c.company_name, c.email, c.phone_mobile
                FROM projects p
                LEFT JOIN customers c ON p.customer_id = c.id
            """
        else:
            sql = """
                SELECT 
                    id, project_name, offer_status, offer_sent_date,
                    offer_accepted_date, offer_rejected_date, offer_version,
                    offer_value, rejection_reason, rejection_notes,
                    follow_up_date, follow_up_completed, customer_id
                FROM projects
            """
        
        if status_filter:
            sql += " WHERE p.offer_status = ?" if include_customer_info else " WHERE offer_status = ?"
            cursor.execute(sql, (status_filter))
        else:
            cursor.execute(sql)
        
        offers = []
        for row in cursor.fetchall():
            offer = {
                'id': row[0],
                'project_name': row[1],
                'offer_status': row[2] or 'draft',
                'offer_sent_date': row[3],
                'offer_accepted_date': row[4],
                'offer_rejected_date': row[5],
                'offer_version': row[6] or 1,
                'offer_value': row[7],
                'rejection_reason': row[8],
                'rejection_notes': row[9],
                'follow_up_date': row[10],
                'follow_up_completed': row[11] or 0,
                'customer_id': row[12]
            }
            
            if include_customer_info and len(row) > 13:
                offer['customer_first_name'] = row[13]
                offer['customer_last_name'] = row[14]
                offer['customer_company_name'] = row[15]
                offer['customer_email'] = row[16]
                offer['customer_phone'] = row[17]
            
            offers.append(offer)
        
        return offers
        
    except Exception as e:
        print(f"Fehler beim Laden der Angebote: {e}")
        return []


def get_pending_follow_ups(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """
    Lädt alle Angebote mit ausstehenden Follow-ups.
    
    Returns:
        Liste von Angeboten, die ein Follow-up benötigen
    """
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            SELECT 
                p.id, p.project_name, p.offer_status, p.offer_sent_date,
                p.offer_value, p.follow_up_date, p.customer_id,
                c.first_name, c.last_name, c.company_name, c.email
            FROM projects p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE p.follow_up_date IS NOT NULL
            AND p.follow_up_date <= ?
            AND p.follow_up_completed = 0
            AND p.offer_status IN ('sent', 'draft')
            ORDER BY p.follow_up_date ASC
        """, (now))
        
        follow_ups = []
        for row in cursor.fetchall():
            follow_ups.append({
                'id': row[0],
                'project_name': row[1],
                'offer_status': row[2],
                'offer_sent_date': row[3],
                'offer_value': row[4],
                'follow_up_date': row[5],
                'customer_id': row[6],
                'customer_first_name': row[7],
                'customer_last_name': row[8],
                'customer_company_name': row[9],
                'customer_email': row[10]
            })
        
        return follow_ups
        
    except Exception as e:
        print(f"Fehler beim Laden der Follow-ups: {e}")
        return []


def mark_follow_up_completed(conn: sqlite3.Connection, project_id: int) -> bool:
    """
    Markiert ein Follow-up als erledigt.
    
    Args:
        conn: Datenbankverbindung
        project_id: ID des Projekts
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET follow_up_completed = 1, last_updated = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), project_id))
        conn.commit()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Fehler beim Markieren des Follow-ups: {e}")
        return False


def update_lead_status_from_offer(
    conn: sqlite3.Connection,
    project_id: int,
    offer_status: str
) -> bool:
    """
    Aktualisiert den Lead-Status basierend auf dem Angebotsstatus.
    
    Args:
        conn: Datenbankverbindung
        project_id: ID des Projekts
        offer_status: Angebotsstatus (accepted -> won, rejected -> lost)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Lade Projekt um customer_id zu bekommen
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        customer_id = row[0]
        
        # Prüfe ob crm_leads Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='crm_leads'
        """)
        
        if not cursor.fetchone():
            # Tabelle existiert nicht, überspringe Lead-Update
            return True
        
        # Mappe Angebotsstatus zu Lead-Status
        lead_status_map = {
            'accepted': 'won',
            'rejected': 'lost'
        }
        
        new_lead_status = lead_status_map.get(offer_status)
        
        if new_lead_status:
            cursor.execute("""
                UPDATE crm_leads
                SET stage = ?, stage_changed_at = ?, updated_at = ?
                WHERE id IN (
                    SELECT id FROM crm_leads
                    WHERE company_name IN (
                        SELECT company_name FROM customers WHERE id = ?
                    )
                    OR contact_person IN (
                        SELECT first_name || ' ' || last_name FROM customers WHERE id = ?
                    )
                )
            """, (new_lead_status, datetime.now().isoformat(), 
                  datetime.now().isoformat(), customer_id, customer_id))
            conn.commit()
        
        return True
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Lead-Status: {e}")
        return False


def get_offer_statistics(conn: sqlite3.Connection) -> dict[str, Any]:
    """
    Berechnet Statistiken über Angebote.
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        cursor = conn.cursor()
        
        # Gesamtanzahl Angebote
        cursor.execute("SELECT COUNT(*) FROM projects WHERE offer_status IS NOT NULL")
        total_offers = cursor.fetchone()[0]
        
        # Angebote nach Status
        cursor.execute("""
            SELECT offer_status, COUNT(*) as count
            FROM projects
            WHERE offer_status IS NOT NULL
            GROUP BY offer_status
        """)
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Durchschnittlicher Angebotswert
        cursor.execute("""
            SELECT AVG(offer_value)
            FROM projects
            WHERE offer_value IS NOT NULL AND offer_value > 0
        """)
        avg_value = cursor.fetchone()[0] or 0
        
        # Conversion Rate (accepted / (accepted + rejected))
        accepted = status_counts.get('accepted', 0)
        rejected = status_counts.get('rejected', 0)
        total_closed = accepted + rejected
        if total_closed != 0:
            conversion_rate = (accepted / total_closed * 100) if total_closed > 0 else 0
        else:
            conversion_rate = 0.0
        
        # Ausstehende Follow-ups
        cursor.execute("""
            SELECT COUNT(*)
            FROM projects
            WHERE follow_up_date IS NOT NULL
            AND follow_up_date <= ?
            AND follow_up_completed = 0
        """, (datetime.now().isoformat()))
        pending_follow_ups = cursor.fetchone()[0]
        
        return {
            'total_offers': total_offers,
            'draft': status_counts.get('draft', 0),
            'sent': status_counts.get('sent', 0),
            'accepted': status_counts.get('accepted', 0),
            'rejected': status_counts.get('rejected', 0),
            'avg_offer_value': avg_value,
            'conversion_rate': conversion_rate,
            'pending_follow_ups': pending_follow_ups
        }
        
    except Exception as e:
        print(f"Fehler beim Berechnen der Statistiken: {e}")
        return {
            'total_offers': 0,
            'draft': 0,
            'sent': 0,
            'accepted': 0,
            'rejected': 0,
            'avg_offer_value': 0,
            'conversion_rate': 0,
            'pending_follow_ups': 0
        }
