# crm/features/contract_manager.py
"""
Vertrags- und Garantieverwaltung für CRM
Ermöglicht Verwaltung von Verträgen und Garantien mit automatischen Ablauf-Erinnerungen

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Any


def create_contract_tables(conn: sqlite3.Connection) -> None:
    """Erstellt die Tabellen für Vertrags- und Garantieverwaltung.
    
    Args:
        conn: SQLite Datenbankverbindung
    """
    cursor = conn.cursor()
    
    try:
        # 1. Tabelle: contracts (Verträge)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                contract_type TEXT NOT NULL,
                contract_number TEXT,
                title TEXT NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                end_date DATE,
                value REAL,
                currency TEXT DEFAULT 'EUR',
                status TEXT DEFAULT 'active',
                document_id INTEGER,
                renewal_type TEXT,
                notice_period_days INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (document_id) REFERENCES customer_documents(id) ON DELETE SET NULL
            )
        """)
        print("DB: Tabelle 'contracts' erstellt/überprüft.")
        
        # 2. Tabelle: warranties (Garantien)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warranties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                warranty_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                duration_months INTEGER NOT NULL,
                end_date DATE,
                terms TEXT,
                coverage_details TEXT,
                provider TEXT,
                provider_contact TEXT,
                document_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT,
                notes TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES customer_documents(id) ON DELETE SET NULL
            )
        """)
        print("DB: Tabelle 'warranties' erstellt/überprüft.")
        
        # 3. Tabelle: contract_reminders (Ablauf-Erinnerungen)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contract_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER,
                warranty_id INTEGER,
                reminder_type TEXT NOT NULL,
                reminder_date DATE NOT NULL,
                status TEXT DEFAULT 'pending',
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified_at TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
                FOREIGN KEY (warranty_id) REFERENCES warranties(id) ON DELETE CASCADE
            )
        """)
        print("DB: Tabelle 'contract_reminders' erstellt/überprüft.")
        
        # 4. Indizes für Performance
        indices = [
            ("idx_contracts_customer_id", "contracts", "customer_id"),
            ("idx_contracts_project_id", "contracts", "project_id"),
            ("idx_contracts_status", "contracts", "status"),
            ("idx_contracts_end_date", "contracts", "end_date"),
            ("idx_warranties_project_id", "warranties", "project_id"),
            ("idx_warranties_customer_id", "warranties", "customer_id"),
            ("idx_warranties_status", "warranties", "status"),
            ("idx_warranties_end_date", "warranties", "end_date"),
            ("idx_contract_reminders_date", "contract_reminders", "reminder_date"),
            ("idx_contract_reminders_status", "contract_reminders", "status"),
        ]
        
        for index_name, table_name, column_name in indices:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
            except sqlite3.OperationalError:
                pass  # Index existiert bereits
        
        conn.commit()
        print("DB: Vertrags- und Garantie-Tabellen erfolgreich erstellt/aktualisiert.")
        
    except Exception as e:
        print(f"DB FEHLER beim Erstellen der Vertrags-Tabellen: {e}")
        conn.rollback()
        raise


# ============================================================================
# CONTRACT CRUD OPERATIONS
# ============================================================================

def create_contract(
    conn: sqlite3.Connection,
    customer_id: int,
    contract_type: str,
    title: str,
    start_date: str,
    end_date: str | None = None,
    project_id: int | None = None,
    contract_number: str | None = None,
    description: str | None = None,
    value: float | None = None,
    currency: str = 'EUR',
    status: str = 'active',
    document_id: int | None = None,
    renewal_type: str | None = None,
    notice_period_days: int | None = None,
    notes: str | None = None,
    created_by: str | None = None
) -> int | None:
    """Erstellt einen neuen Vertrag.
    
    Args:
        conn: Datenbankverbindung
        customer_id: Kunden-ID
        contract_type: Vertragstyp (z.B. 'Wartungsvertrag', 'Kaufvertrag', 'Mietvertrag')
        title: Vertragstitel
        start_date: Startdatum (YYYY-MM-DD)
        end_date: Enddatum (YYYY-MM-DD, optional)
        project_id: Projekt-ID (optional)
        contract_number: Vertragsnummer (optional)
        description: Beschreibung (optional)
        value: Vertragswert (optional)
        currency: Währung (Standard: EUR)
        status: Status (Standard: active)
        document_id: Verknüpftes Dokument (optional)
        renewal_type: Verlängerungstyp (optional)
        notice_period_days: Kündigungsfrist in Tagen (optional)
        notes: Notizen (optional)
        created_by: Ersteller (optional)
    
    Returns:
        Vertrags-ID bei Erfolg, None bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contracts 
            (customer_id, project_id, contract_type, contract_number, title, description,
             start_date, end_date, value, currency, status, document_id, renewal_type,
             notice_period_days, notes, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, project_id, contract_type, contract_number, title, description,
              start_date, end_date, value, currency, status, document_id, renewal_type,
              notice_period_days, notes, created_by, created_by))
        
        contract_id = cursor.lastrowid
        
        # Erstelle automatische Erinnerung wenn Enddatum vorhanden
        if end_date:
            create_contract_expiry_reminder(conn, contract_id, end_date)
        
        conn.commit()
        print(f"Vertrag erstellt: {title} (ID: {contract_id})")
        return contract_id
    except Exception as e:
        print(f"Fehler beim Erstellen des Vertrags: {e}")
        conn.rollback()
        return None


def get_contract_by_id(conn: sqlite3.Connection, contract_id: int) -> dict[str, Any] | None:
    """Lädt einen Vertrag anhand der ID.
    
    Args:
        conn: Datenbankverbindung
        contract_id: Vertrags-ID
    
    Returns:
        Vertrags-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Fehler beim Laden des Vertrags: {e}")
        return None


def get_contracts_by_customer(
    conn: sqlite3.Connection,
    customer_id: int,
    status: str | None = None
) -> list[dict[str, Any]]:
    """Lädt alle Verträge eines Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_id: Kunden-ID
        status: Nur Verträge mit diesem Status (optional)
    
    Returns:
        Liste von Vertrags-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM contracts WHERE customer_id = ?"
        params = [customer_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY start_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Verträge: {e}")
        return []



def get_contracts_by_project(
    conn: sqlite3.Connection,
    project_id: int
) -> list[dict[str, Any]]:
    """Lädt alle Verträge eines Projekts.
    
    Args:
        conn: Datenbankverbindung
        project_id: Projekt-ID
    
    Returns:
        Liste von Vertrags-Dictionaries
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contracts 
            WHERE project_id = ?
            ORDER BY start_date DESC
        """, (project_id))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Projekt-Verträge: {e}")
        return []


def get_all_contracts(
    conn: sqlite3.Connection,
    status: str | None = None,
    contract_type: str | None = None
) -> list[dict[str, Any]]:
    """Lädt alle Verträge.
    
    Args:
        conn: Datenbankverbindung
        status: Nur Verträge mit diesem Status (optional)
        contract_type: Nur Verträge dieses Typs (optional)
    
    Returns:
        Liste von Vertrags-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM contracts WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if contract_type:
            query += " AND contract_type = ?"
            params.append(contract_type)
        
        query += " ORDER BY start_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Verträge: {e}")
        return []


def update_contract(
    conn: sqlite3.Connection,
    contract_id: int,
    **kwargs
) -> bool:
    """Aktualisiert einen Vertrag.
    
    Args:
        conn: Datenbankverbindung
        contract_id: Vertrags-ID
        **kwargs: Zu aktualisierende Felder
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        if not kwargs:
            return True
        
        # Baue UPDATE-Statement dynamisch
        updates = []
        params = []
        
        allowed_fields = [
            'contract_type', 'contract_number', 'title', 'description',
            'start_date', 'end_date', 'value', 'currency', 'status',
            'document_id', 'renewal_type', 'notice_period_days', 'notes',
            'updated_by', 'project_id'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return True
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(contract_id)
        
        cursor = conn.cursor()
        query = f"UPDATE contracts SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        # Aktualisiere Erinnerungen wenn Enddatum geändert wurde
        if 'end_date' in kwargs and kwargs['end_date']:
            update_contract_expiry_reminder(conn, contract_id, kwargs['end_date'])
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Vertrags: {e}")
        conn.rollback()
        return False



def delete_contract(conn: sqlite3.Connection, contract_id: int) -> bool:
    """Löscht einen Vertrag.
    
    Args:
        conn: Datenbankverbindung
        contract_id: Vertrags-ID
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id))
        conn.commit()
        print(f"Vertrag gelöscht (ID: {contract_id})")
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Löschen des Vertrags: {e}")
        conn.rollback()
        return False


# ============================================================================
# WARRANTY CRUD OPERATIONS
# ============================================================================

def create_warranty(
    conn: sqlite3.Connection,
    project_id: int,
    customer_id: int,
    warranty_type: str,
    title: str,
    start_date: str,
    duration_months: int,
    description: str | None = None,
    terms: str | None = None,
    coverage_details: str | None = None,
    provider: str | None = None,
    provider_contact: str | None = None,
    document_id: int | None = None,
    status: str = 'active',
    notes: str | None = None,
    created_by: str | None = None
) -> int | None:
    """Erstellt eine neue Garantie.
    
    Args:
        conn: Datenbankverbindung
        project_id: Projekt-ID
        customer_id: Kunden-ID
        warranty_type: Garantietyp (z.B. 'Produktgarantie', 'Leistungsgarantie', 'Herstellergarantie')
        title: Garantietitel
        start_date: Startdatum (YYYY-MM-DD)
        duration_months: Laufzeit in Monaten
        description: Beschreibung (optional)
        terms: Garantiebedingungen (optional)
        coverage_details: Abdeckungsdetails (optional)
        provider: Garantiegeber (optional)
        provider_contact: Kontakt des Garantiegebers (optional)
        document_id: Verknüpftes Dokument (optional)
        status: Status (Standard: active)
        notes: Notizen (optional)
        created_by: Ersteller (optional)
    
    Returns:
        Garantie-ID bei Erfolg, None bei Fehler
    """
    try:
        # Berechne Enddatum
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = start + timedelta(days=duration_months * 30)  # Approximation
        end_date = end.strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO warranties 
            (project_id, customer_id, warranty_type, title, description, start_date,
             duration_months, end_date, terms, coverage_details, provider, provider_contact,
             document_id, status, notes, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, customer_id, warranty_type, title, description, start_date,
              duration_months, end_date, terms, coverage_details, provider, provider_contact,
              document_id, status, notes, created_by, created_by))
        
        warranty_id = cursor.lastrowid
        
        # Erstelle automatische Erinnerung
        create_warranty_expiry_reminder(conn, warranty_id, end_date)
        
        conn.commit()
        print(f"Garantie erstellt: {title} (ID: {warranty_id})")
        return warranty_id
    except Exception as e:
        print(f"Fehler beim Erstellen der Garantie: {e}")
        conn.rollback()
        return None



def get_warranty_by_id(conn: sqlite3.Connection, warranty_id: int) -> dict[str, Any] | None:
    """Lädt eine Garantie anhand der ID.
    
    Args:
        conn: Datenbankverbindung
        warranty_id: Garantie-ID
    
    Returns:
        Garantie-Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM warranties WHERE id = ?", (warranty_id))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Fehler beim Laden der Garantie: {e}")
        return None


def get_warranties_by_project(
    conn: sqlite3.Connection,
    project_id: int,
    status: str | None = None
) -> list[dict[str, Any]]:
    """Lädt alle Garantien eines Projekts.
    
    Args:
        conn: Datenbankverbindung
        project_id: Projekt-ID
        status: Nur Garantien mit diesem Status (optional)
    
    Returns:
        Liste von Garantie-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM warranties WHERE project_id = ?"
        params = [project_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY start_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Garantien: {e}")
        return []


def get_warranties_by_customer(
    conn: sqlite3.Connection,
    customer_id: int,
    status: str | None = None
) -> list[dict[str, Any]]:
    """Lädt alle Garantien eines Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_id: Kunden-ID
        status: Nur Garantien mit diesem Status (optional)
    
    Returns:
        Liste von Garantie-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM warranties WHERE customer_id = ?"
        params = [customer_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY start_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Kunden-Garantien: {e}")
        return []


def get_all_warranties(
    conn: sqlite3.Connection,
    status: str | None = None,
    warranty_type: str | None = None
) -> list[dict[str, Any]]:
    """Lädt alle Garantien.
    
    Args:
        conn: Datenbankverbindung
        status: Nur Garantien mit diesem Status (optional)
        warranty_type: Nur Garantien dieses Typs (optional)
    
    Returns:
        Liste von Garantie-Dictionaries
    """
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM warranties WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if warranty_type:
            query += " AND warranty_type = ?"
            params.append(warranty_type)
        
        query += " ORDER BY start_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Garantien: {e}")
        return []



def update_warranty(
    conn: sqlite3.Connection,
    warranty_id: int,
    **kwargs
) -> bool:
    """Aktualisiert eine Garantie.
    
    Args:
        conn: Datenbankverbindung
        warranty_id: Garantie-ID
        **kwargs: Zu aktualisierende Felder
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        if not kwargs:
            return True
        
        # Baue UPDATE-Statement dynamisch
        updates = []
        params = []
        
        allowed_fields = [
            'warranty_type', 'title', 'description', 'start_date', 'duration_months',
            'end_date', 'terms', 'coverage_details', 'provider', 'provider_contact',
            'document_id', 'status', 'notes', 'updated_by', 'project_id', 'customer_id'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return True
        
        # Wenn duration_months geändert wurde, berechne neues end_date
        if 'duration_months' in kwargs or 'start_date' in kwargs:
            warranty = get_warranty_by_id(conn, warranty_id)
            if warranty:
                start_date = kwargs.get('start_date', warranty['start_date'])
                duration = kwargs.get('duration_months', warranty['duration_months'])
                
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = start + timedelta(days=duration * 30)
                end_date = end.strftime('%Y-%m-%d')
                
                updates.append("end_date = ?")
                params.append(end_date)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(warranty_id)
        
        cursor = conn.cursor()
        query = f"UPDATE warranties SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        # Aktualisiere Erinnerungen wenn Enddatum geändert wurde
        if 'end_date' in kwargs or 'duration_months' in kwargs or 'start_date' in kwargs:
            warranty = get_warranty_by_id(conn, warranty_id)
            if warranty and warranty['end_date']:
                update_warranty_expiry_reminder(conn, warranty_id, warranty['end_date'])
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Garantie: {e}")
        conn.rollback()
        return False


def delete_warranty(conn: sqlite3.Connection, warranty_id: int) -> bool:
    """Löscht eine Garantie.
    
    Args:
        conn: Datenbankverbindung
        warranty_id: Garantie-ID
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warranties WHERE id = ?", (warranty_id))
        conn.commit()
        print(f"Garantie gelöscht (ID: {warranty_id})")
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Löschen der Garantie: {e}")
        conn.rollback()
        return False



# ============================================================================
# REMINDER MANAGEMENT
# ============================================================================

def create_contract_expiry_reminder(
    conn: sqlite3.Connection,
    contract_id: int,
    end_date: str,
    days_before: int = 30
) -> int | None:
    """Erstellt eine Ablauf-Erinnerung für einen Vertrag.
    
    Args:
        conn: Datenbankverbindung
        contract_id: Vertrags-ID
        end_date: Enddatum des Vertrags (YYYY-MM-DD)
        days_before: Tage vor Ablauf für Erinnerung (Standard: 30)
    
    Returns:
        Erinnerungs-ID bei Erfolg, None bei Fehler
    """
    try:
        # Berechne Erinnerungsdatum
        end = datetime.strptime(end_date, '%Y-%m-%d')
        reminder_date = end - timedelta(days=days_before)
        reminder_date_str = reminder_date.strftime('%Y-%m-%d')
        
        # Prüfe ob bereits eine Erinnerung existiert
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM contract_reminders 
            WHERE contract_id = ? AND reminder_type = 'contract_expiry'
        """, (contract_id))
        existing = cursor.fetchone()
        
        if existing:
            # Aktualisiere bestehende Erinnerung
            cursor.execute("""
                UPDATE contract_reminders 
                SET reminder_date = ?, status = 'pending', notified_at = NULL
                WHERE id = ?
            """, (reminder_date_str, existing[0]))
            conn.commit()
            return existing[0]
        else:
            # Erstelle neue Erinnerung
            cursor.execute("""
                INSERT INTO contract_reminders 
                (contract_id, reminder_type, reminder_date, message)
                VALUES (?, 'contract_expiry', ?, ?)
            """, (contract_id, reminder_date_str, 
                  f"Vertrag läuft in {days_before} Tagen ab"))
            
            reminder_id = cursor.lastrowid
            conn.commit()
            return reminder_id
    except Exception as e:
        print(f"Fehler beim Erstellen der Vertrags-Erinnerung: {e}")
        conn.rollback()
        return None


def create_warranty_expiry_reminder(
    conn: sqlite3.Connection,
    warranty_id: int,
    end_date: str,
    days_before: int = 30
) -> int | None:
    """Erstellt eine Ablauf-Erinnerung für eine Garantie.
    
    Args:
        conn: Datenbankverbindung
        warranty_id: Garantie-ID
        end_date: Enddatum der Garantie (YYYY-MM-DD)
        days_before: Tage vor Ablauf für Erinnerung (Standard: 30)
    
    Returns:
        Erinnerungs-ID bei Erfolg, None bei Fehler
    """
    try:
        # Berechne Erinnerungsdatum
        end = datetime.strptime(end_date, '%Y-%m-%d')
        reminder_date = end - timedelta(days=days_before)
        reminder_date_str = reminder_date.strftime('%Y-%m-%d')
        
        # Prüfe ob bereits eine Erinnerung existiert
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM contract_reminders 
            WHERE warranty_id = ? AND reminder_type = 'warranty_expiry'
        """, (warranty_id))
        existing = cursor.fetchone()
        
        if existing:
            # Aktualisiere bestehende Erinnerung
            cursor.execute("""
                UPDATE contract_reminders 
                SET reminder_date = ?, status = 'pending', notified_at = NULL
                WHERE id = ?
            """, (reminder_date_str, existing[0]))
            conn.commit()
            return existing[0]
        else:
            # Erstelle neue Erinnerung
            cursor.execute("""
                INSERT INTO contract_reminders 
                (warranty_id, reminder_type, reminder_date, message)
                VALUES (?, 'warranty_expiry', ?, ?)
            """, (warranty_id, reminder_date_str, 
                  f"Garantie läuft in {days_before} Tagen ab"))
            
            reminder_id = cursor.lastrowid
            conn.commit()
            return reminder_id
    except Exception as e:
        print(f"Fehler beim Erstellen der Garantie-Erinnerung: {e}")
        conn.rollback()
        return None



def update_contract_expiry_reminder(
    conn: sqlite3.Connection,
    contract_id: int,
    end_date: str,
    days_before: int = 30
) -> bool:
    """Aktualisiert die Ablauf-Erinnerung für einen Vertrag.
    
    Args:
        conn: Datenbankverbindung
        contract_id: Vertrags-ID
        end_date: Neues Enddatum (YYYY-MM-DD)
        days_before: Tage vor Ablauf (Standard: 30)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        create_contract_expiry_reminder(conn, contract_id, end_date, days_before)
        return True
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Vertrags-Erinnerung: {e}")
        return False


def update_warranty_expiry_reminder(
    conn: sqlite3.Connection,
    warranty_id: int,
    end_date: str,
    days_before: int = 30
) -> bool:
    """Aktualisiert die Ablauf-Erinnerung für eine Garantie.
    
    Args:
        conn: Datenbankverbindung
        warranty_id: Garantie-ID
        end_date: Neues Enddatum (YYYY-MM-DD)
        days_before: Tage vor Ablauf (Standard: 30)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        create_warranty_expiry_reminder(conn, warranty_id, end_date, days_before)
        return True
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Garantie-Erinnerung: {e}")
        return False


def get_pending_reminders(
    conn: sqlite3.Connection,
    days_ahead: int = 7
) -> list[dict[str, Any]]:
    """Lädt alle fälligen Erinnerungen.
    
    Args:
        conn: Datenbankverbindung
        days_ahead: Tage in die Zukunft (Standard: 7)
    
    Returns:
        Liste von Erinnerungs-Dictionaries mit Details
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                cr.*,
                c.title as contract_title,
                c.customer_id as contract_customer_id,
                w.title as warranty_title,
                w.customer_id as warranty_customer_id,
                w.project_id as warranty_project_id
            FROM contract_reminders cr
            LEFT JOIN contracts c ON cr.contract_id = c.id
            LEFT JOIN warranties w ON cr.warranty_id = w.id
            WHERE cr.status = 'pending'
            AND cr.reminder_date BETWEEN ? AND ?
            ORDER BY cr.reminder_date ASC
        """, (today, future_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der fälligen Erinnerungen: {e}")
        return []


def mark_reminder_notified(
    conn: sqlite3.Connection,
    reminder_id: int
) -> bool:
    """Markiert eine Erinnerung als benachrichtigt.
    
    Args:
        conn: Datenbankverbindung
        reminder_id: Erinnerungs-ID
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contract_reminders 
            SET status = 'notified', notified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reminder_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler beim Markieren der Erinnerung: {e}")
        conn.rollback()
        return False



# ============================================================================
# EXPIRING CONTRACTS & WARRANTIES
# ============================================================================

def get_expiring_contracts(
    conn: sqlite3.Connection,
    days_ahead: int = 30
) -> list[dict[str, Any]]:
    """Lädt alle Verträge, die in den nächsten X Tagen ablaufen.
    
    Args:
        conn: Datenbankverbindung
        days_ahead: Tage in die Zukunft (Standard: 30)
    
    Returns:
        Liste von Vertrags-Dictionaries
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contracts 
            WHERE status = 'active'
            AND end_date IS NOT NULL
            AND end_date BETWEEN ? AND ?
            ORDER BY end_date ASC
        """, (today, future_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der ablaufenden Verträge: {e}")
        return []


def get_expiring_warranties(
    conn: sqlite3.Connection,
    days_ahead: int = 30
) -> list[dict[str, Any]]:
    """Lädt alle Garantien, die in den nächsten X Tagen ablaufen.
    
    Args:
        conn: Datenbankverbindung
        days_ahead: Tage in die Zukunft (Standard: 30)
    
    Returns:
        Liste von Garantie-Dictionaries
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM warranties 
            WHERE status = 'active'
            AND end_date BETWEEN ? AND ?
            ORDER BY end_date ASC
        """, (today, future_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der ablaufenden Garantien: {e}")
        return []


def get_expired_contracts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Lädt alle abgelaufenen Verträge.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Vertrags-Dictionaries
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contracts 
            WHERE status = 'active'
            AND end_date IS NOT NULL
            AND end_date < ?
            ORDER BY end_date DESC
        """, (today))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der abgelaufenen Verträge: {e}")
        return []


def get_expired_warranties(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Lädt alle abgelaufenen Garantien.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Garantie-Dictionaries
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM warranties 
            WHERE status = 'active'
            AND end_date < ?
            ORDER BY end_date DESC
        """, (today))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der abgelaufenen Garantien: {e}")
        return []



# ============================================================================
# STATISTICS & UTILITIES
# ============================================================================

def get_contract_statistics(conn: sqlite3.Connection) -> dict[str, Any]:
    """Lädt Statistiken über Verträge.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        cursor = conn.cursor()
        
        # Gesamtanzahl
        cursor.execute("SELECT COUNT(*) FROM contracts")
        total = cursor.fetchone()[0]
        
        # Nach Status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM contracts
            GROUP BY status
        """)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Nach Typ
        cursor.execute("""
            SELECT contract_type, COUNT(*) as count
            FROM contracts
            GROUP BY contract_type
            ORDER BY count DESC
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Ablaufende Verträge (30 Tage)
        expiring = len(get_expiring_contracts(conn, 30))
        
        # Abgelaufene Verträge
        expired = len(get_expired_contracts(conn))
        
        # Gesamtwert aktiver Verträge
        cursor.execute("""
            SELECT SUM(value) FROM contracts 
            WHERE status = 'active' AND value IS NOT NULL
        """)
        total_value = cursor.fetchone()[0] or 0
        
        return {
            'total': total,
            'by_status': by_status,
            'by_type': by_type,
            'expiring_30_days': expiring,
            'expired': expired,
            'total_value': total_value
        }
    except Exception as e:
        print(f"Fehler beim Laden der Vertrags-Statistiken: {e}")
        return {
            'total': 0,
            'by_status': {},
            'by_type': {},
            'expiring_30_days': 0,
            'expired': 0,
            'total_value': 0
        }


def get_warranty_statistics(conn: sqlite3.Connection) -> dict[str, Any]:
    """Lädt Statistiken über Garantien.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        cursor = conn.cursor()
        
        # Gesamtanzahl
        cursor.execute("SELECT COUNT(*) FROM warranties")
        total = cursor.fetchone()[0]
        
        # Nach Status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM warranties
            GROUP BY status
        """)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Nach Typ
        cursor.execute("""
            SELECT warranty_type, COUNT(*) as count
            FROM warranties
            GROUP BY warranty_type
            ORDER BY count DESC
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Ablaufende Garantien (30 Tage)
        expiring = len(get_expiring_warranties(conn, 30))
        
        # Abgelaufene Garantien
        expired = len(get_expired_warranties(conn))
        
        return {
            'total': total,
            'by_status': by_status,
            'by_type': by_type,
            'expiring_30_days': expiring,
            'expired': expired
        }
    except Exception as e:
        print(f"Fehler beim Laden der Garantie-Statistiken: {e}")
        return {
            'total': 0,
            'by_status': {},
            'by_type': {},
            'expiring_30_days': 0,
            'expired': 0
        }


def get_contract_types(conn: sqlite3.Connection) -> list[str]:
    """Lädt alle verwendeten Vertragstypen.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Vertragstypen
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT contract_type 
            FROM contracts 
            WHERE contract_type IS NOT NULL AND contract_type != ''
            ORDER BY contract_type ASC
        """)
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Vertragstypen: {e}")
        return []


def get_warranty_types(conn: sqlite3.Connection) -> list[str]:
    """Lädt alle verwendeten Garantietypen.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Liste von Garantietypen
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT warranty_type 
            FROM warranties 
            WHERE warranty_type IS NOT NULL AND warranty_type != ''
            ORDER BY warranty_type ASC
        """)
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Fehler beim Laden der Garantietypen: {e}")
        return []


# ============================================================================
# INITIALIZATION
# ============================================================================

def ensure_contract_tables() -> None:
    """Stellt sicher, dass die Vertrags- und Garantie-Tabellen existieren."""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            create_contract_tables(conn)
            conn.close()
    except Exception as e:
        print(f"Fehler beim Initialisieren der Vertrags-Tabellen: {e}")


# Initialisiere Tabellen beim Import
try:
    ensure_contract_tables()
except Exception:
    pass  # Fehler beim Import ignorieren
