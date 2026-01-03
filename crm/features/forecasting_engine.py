"""
CRM Forecasting Engine
Verkaufsziele und Forecasting-System

Autor: Kiro AI
Datum: 2025-01-14
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Any, Optional
import json

try:
    from database import get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    def get_db_connection():
        return None


def create_forecasting_tables(conn: Optional[sqlite3.Connection] = None) -> bool:
    """
    Erstellt die Tabellen für Verkaufsziele und Forecasts.
    
    Args:
        conn: Optionale Datenbankverbindung
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    if not DATABASE_AVAILABLE:
        return False
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tabelle für Verkaufsziele
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_name TEXT NOT NULL,
                target_type TEXT NOT NULL, -- 'individual', 'team', 'company'
                assigned_to TEXT, -- Mitarbeiter-Name oder NULL für Team/Company
                period_type TEXT NOT NULL, -- 'monthly', 'quarterly', 'yearly'
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                target_value REAL NOT NULL, -- Zielwert in EUR
                target_unit TEXT DEFAULT 'EUR', -- 'EUR', 'deals', 'leads'
                current_value REAL DEFAULT 0, -- Aktueller Wert
                status TEXT DEFAULT 'active', -- 'active', 'completed', 'failed', 'cancelled'
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        """)
        
        # Tabelle für Forecasts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER, -- Verknüpfung zu sales_targets (optional)
                forecast_period TEXT NOT NULL, -- 'monthly', 'quarterly', 'yearly'
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                forecast_value REAL NOT NULL, -- Prognostizierter Wert
                confidence_level REAL, -- 0.0 - 1.0 (Konfidenz der Prognose)
                forecast_method TEXT, -- 'pipeline_based', 'historical', 'manual'
                pipeline_data TEXT, -- JSON mit Pipeline-Daten
                calculation_details TEXT, -- JSON mit Berechnungsdetails
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY(target_id) REFERENCES sales_targets(id)
            )
        """)
        
        # Indizes für Performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_targets_period 
            ON sales_targets(period_start, period_end)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_targets_assigned 
            ON sales_targets(assigned_to)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_forecasts_period 
            ON sales_forecasts(period_start, period_end)
        """)
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Fehler beim Erstellen der Forecasting-Tabellen: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if close_conn and conn:
            conn.close()


def ensure_forecasting_tables() -> bool:
    """Stellt sicher, dass die Forecasting-Tabellen existieren."""
    return create_forecasting_tables()


# ============================================================================
# VERKAUFSZIELE (Sales Targets)
# ============================================================================

def create_sales_target(
    target_name: str,
    target_type: str,
    period_type: str,
    period_start: str,
    period_end: str,
    target_value: float,
    assigned_to: Optional[str] = None,
    target_unit: str = 'EUR',
    description: Optional[str] = None,
    created_by: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> Optional[int]:
    """
    Erstellt ein neues Verkaufsziel.
    
    Args:
        target_name: Name des Ziels
        target_type: 'individual', 'team', 'company'
        period_type: 'monthly', 'quarterly', 'yearly'
        period_start: Start-Datum (YYYY-MM-DD)
        period_end: End-Datum (YYYY-MM-DD)
        target_value: Zielwert
        assigned_to: Mitarbeiter-Name (nur bei 'individual')
        target_unit: Einheit ('EUR', 'deals', 'leads')
        description: Beschreibung
        created_by: Ersteller
        conn: Optionale Datenbankverbindung
        
    Returns:
        int: ID des erstellten Ziels oder None bei Fehler
    """
    if not DATABASE_AVAILABLE:
        return None
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sales_targets (
                target_name, target_type, assigned_to, period_type,
                period_start, period_end, target_value, target_unit,
                description, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_name, target_type, assigned_to, period_type,
            period_start, period_end, target_value, target_unit,
            description, created_by
        ))
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Verkaufsziels: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if close_conn and conn:
            conn.close()


def get_sales_targets(
    target_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> list[dict[str, Any]]:
    """
    Lädt Verkaufsziele mit optionalen Filtern.
    
    Args:
        target_type: Filter nach Typ
        assigned_to: Filter nach Mitarbeiter
        status: Filter nach Status
        period_start: Filter nach Start-Datum
        period_end: Filter nach End-Datum
        conn: Optionale Datenbankverbindung
        
    Returns:
        list: Liste von Verkaufszielen
    """
    if not DATABASE_AVAILABLE:
        return []
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM sales_targets WHERE 1=1"
        params = []
        
        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)
        
        if assigned_to:
            query += " AND assigned_to = ?"
            params.append(assigned_to)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if period_start:
            query += " AND period_end >= ?"
            params.append(period_start)
        
        if period_end:
            query += " AND period_start <= ?"
            params.append(period_end)
        
        query += " ORDER BY period_start DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        targets = []
        for row in rows:
            targets.append({
                'id': row[0],
                'target_name': row[1],
                'target_type': row[2],
                'assigned_to': row[3],
                'period_type': row[4],
                'period_start': row[5],
                'period_end': row[6],
                'target_value': row[7],
                'target_unit': row[8],
                'current_value': row[9],
                'status': row[10],
                'description': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'created_by': row[14]
            })
        
        return targets
        
    except Exception as e:
        print(f"Fehler beim Laden der Verkaufsziele: {e}")
        return []
    finally:
        if close_conn and conn:
            conn.close()


def update_target_progress(
    target_id: int,
    current_value: float,
    conn: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Aktualisiert den Fortschritt eines Verkaufsziels.
    
    Args:
        target_id: ID des Ziels
        current_value: Aktueller Wert
        conn: Optionale Datenbankverbindung
        
    Returns:
        bool: True bei Erfolg
    """
    if not DATABASE_AVAILABLE:
        return False
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sales_targets 
            SET current_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (current_value, target_id))
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Zielfortschritts: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if close_conn and conn:
            conn.close()


def update_target_status(
    target_id: int,
    status: str,
    conn: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Aktualisiert den Status eines Verkaufsziels.
    
    Args:
        target_id: ID des Ziels
        status: Neuer Status ('active', 'completed', 'failed', 'cancelled')
        conn: Optionale Datenbankverbindung
        
    Returns:
        bool: True bei Erfolg
    """
    if not DATABASE_AVAILABLE:
        return False
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sales_targets 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, target_id))
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Zielstatus: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if close_conn and conn:
            conn.close()


# ============================================================================
# FORECASTING
# ============================================================================

def calculate_pipeline_forecast(
    period_start: str,
    period_end: str,
    conn: Optional[sqlite3.Connection] = None
) -> dict[str, Any]:
    """
    Berechnet einen Forecast basierend auf Pipeline-Daten.
    
    Args:
        period_start: Start-Datum (YYYY-MM-DD)
        period_end: End-Datum (YYYY-MM-DD)
        conn: Optionale Datenbankverbindung
        
    Returns:
        dict: Forecast-Daten mit Wert und Konfidenz
    """
    if not DATABASE_AVAILABLE:
        return {'forecast_value': 0, 'confidence_level': 0, 'details': {}}
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return {'forecast_value': 0, 'confidence_level': 0, 'details': {}}
    
    try:
        cursor = conn.cursor()
        
        # Lade Pipeline-Daten (Leads)
        cursor.execute("""
            SELECT stage, estimated_value, probability
            FROM crm_leads
            WHERE status = 'active'
            AND created_at <= ?
        """, (period_end))
        
        leads = cursor.fetchall()
        
        # Wahrscheinlichkeits-Gewichtung nach Stage
        stage_probabilities = {
            'lead': 0.10,
            'qualified': 0.25,
            'proposal': 0.50,
            'negotiation': 0.75,
            'won': 1.0,
            'lost': 0.0
        }
        
        total_weighted_value = 0
        total_leads = 0
        stage_breakdown = {}
        
        for lead in leads:
            stage = lead[0] if lead[0] else 'lead'
            estimated_value = lead[1] if lead[1] else 0
            probability = stage_probabilities.get(stage, 0.10)
            
            weighted_value = estimated_value * probability
            total_weighted_value += weighted_value
            total_leads += 1
            
            if stage not in stage_breakdown:
                stage_breakdown[stage] = {
                    'count': 0,
                    'total_value': 0,
                    'weighted_value': 0
                }
            
            stage_breakdown[stage]['count'] += 1
            stage_breakdown[stage]['total_value'] += estimated_value
            stage_breakdown[stage]['weighted_value'] += weighted_value
        
        # Berechne Konfidenz basierend auf Anzahl der Leads
        if total_leads == 0:
            confidence = 0.0
        elif total_leads < 5:
            confidence = 0.3
        elif total_leads < 10:
            confidence = 0.5
        elif total_leads < 20:
            confidence = 0.7
        else:
            confidence = 0.85
        
        return {
            'forecast_value': round(total_weighted_value, 2),
            'confidence_level': confidence,
            'details': {
                'total_leads': total_leads,
                'stage_breakdown': stage_breakdown,
                'period_start': period_start,
                'period_end': period_end
            }
        }
        
    except Exception as e:
        print(f"Fehler beim Berechnen des Pipeline-Forecasts: {e}")
        return {'forecast_value': 0, 'confidence_level': 0, 'details': {}}
    finally:
        if close_conn and conn:
            conn.close()


def create_forecast(
    forecast_period: str,
    period_start: str,
    period_end: str,
    forecast_value: float,
    confidence_level: float,
    forecast_method: str = 'pipeline_based',
    target_id: Optional[int] = None,
    pipeline_data: Optional[dict] = None,
    calculation_details: Optional[dict] = None,
    notes: Optional[str] = None,
    created_by: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> Optional[int]:
    """
    Erstellt einen neuen Forecast.
    
    Args:
        forecast_period: 'monthly', 'quarterly', 'yearly'
        period_start: Start-Datum (YYYY-MM-DD)
        period_end: End-Datum (YYYY-MM-DD)
        forecast_value: Prognostizierter Wert
        confidence_level: Konfidenz (0.0 - 1.0)
        forecast_method: Methode ('pipeline_based', 'historical', 'manual')
        target_id: Verknüpftes Ziel (optional)
        pipeline_data: Pipeline-Daten als dict
        calculation_details: Berechnungsdetails als dict
        notes: Notizen
        created_by: Ersteller
        conn: Optionale Datenbankverbindung
        
    Returns:
        int: ID des erstellten Forecasts oder None bei Fehler
    """
    if not DATABASE_AVAILABLE:
        return None
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        pipeline_json = json.dumps(pipeline_data) if pipeline_data else None
        details_json = json.dumps(calculation_details) if calculation_details else None
        
        cursor.execute("""
            INSERT INTO sales_forecasts (
                target_id, forecast_period, period_start, period_end,
                forecast_value, confidence_level, forecast_method,
                pipeline_data, calculation_details, notes, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_id, forecast_period, period_start, period_end,
            forecast_value, confidence_level, forecast_method,
            pipeline_json, details_json, notes, created_by
        ))
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Forecasts: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if close_conn and conn:
            conn.close()


def get_forecasts(
    target_id: Optional[int] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> list[dict[str, Any]]:
    """
    Lädt Forecasts mit optionalen Filtern.
    
    Args:
        target_id: Filter nach Ziel-ID
        period_start: Filter nach Start-Datum
        period_end: Filter nach End-Datum
        conn: Optionale Datenbankverbindung
        
    Returns:
        list: Liste von Forecasts
    """
    if not DATABASE_AVAILABLE:
        return []
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM sales_forecasts WHERE 1=1"
        params = []
        
        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)
        
        if period_start:
            query += " AND period_end >= ?"
            params.append(period_start)
        
        if period_end:
            query += " AND period_start <= ?"
            params.append(period_end)
        
        query += " ORDER BY period_start DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        forecasts = []
        for row in rows:
            pipeline_data = json.loads(row[8]) if row[8] else None
            calc_details = json.loads(row[9]) if row[9] else None
            
            forecasts.append({
                'id': row[0],
                'target_id': row[1],
                'forecast_period': row[2],
                'period_start': row[3],
                'period_end': row[4],
                'forecast_value': row[5],
                'confidence_level': row[6],
                'forecast_method': row[7],
                'pipeline_data': pipeline_data,
                'calculation_details': calc_details,
                'notes': row[10],
                'created_at': row[11],
                'created_by': row[12]
            })
        
        return forecasts
        
    except Exception as e:
        print(f"Fehler beim Laden der Forecasts: {e}")
        return []
    finally:
        if close_conn and conn:
            conn.close()


# ============================================================================
# ANALYSE & TRACKING
# ============================================================================

def get_target_achievement_status(
    target_id: int,
    conn: Optional[sqlite3.Connection] = None
) -> dict[str, Any]:
    """
    Berechnet den Zielerreichungsstatus.
    
    Args:
        target_id: ID des Ziels
        conn: Optionale Datenbankverbindung
        
    Returns:
        dict: Status-Informationen
    """
    if not DATABASE_AVAILABLE:
        return {}
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales_targets WHERE id = ?", (target_id,))
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        target_value = row[7]
        current_value = row[9]
        period_start = datetime.strptime(row[5], '%Y-%m-%d')
        period_end = datetime.strptime(row[6], '%Y-%m-%d')
        
        # Berechne Fortschritt
        achievement_percentage = (current_value / target_value * 100) if target_value > 0 else 0
        remaining_value = target_value - current_value
        
        # Berechne Zeitfortschritt
        now = datetime.now()
        total_days = (period_end - period_start).days
        elapsed_days = (now - period_start).days
        time_percentage = (elapsed_days / total_days * 100) if total_days > 0 else 0
        
        # Status-Bewertung
        if achievement_percentage >= 100:
            status = 'achieved'
            health = 'excellent'
        elif achievement_percentage >= time_percentage:
            status = 'on_track'
            health = 'good'
        elif achievement_percentage >= time_percentage * 0.8:
            status = 'at_risk'
            health = 'warning'
        else:
            status = 'off_track'
            health = 'critical'
        
        return {
            'target_id': target_id,
            'target_value': target_value,
            'current_value': current_value,
            'achievement_percentage': round(achievement_percentage, 2),
            'remaining_value': remaining_value,
            'time_percentage': round(time_percentage, 2),
            'status': status,
            'health': health,
            'period_start': row[5],
            'period_end': row[6]
        }
        
    except Exception as e:
        print(f"Fehler beim Berechnen des Zielerreichungsstatus: {e}")
        return {}
    finally:
        if close_conn and conn:
            conn.close()


def check_at_risk_targets(
    conn: Optional[sqlite3.Connection] = None
) -> list[dict[str, Any]]:
    """
    Findet gefährdete Ziele (at_risk oder off_track).
    
    Args:
        conn: Optionale Datenbankverbindung
        
    Returns:
        list: Liste gefährdeter Ziele mit Status
    """
    if not DATABASE_AVAILABLE:
        return []
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM sales_targets 
            WHERE status = 'active'
        """)
        
        target_ids = [row[0] for row in cursor.fetchall()]
        at_risk_targets = []
        
        for target_id in target_ids:
            status = get_target_achievement_status(target_id, conn)
            if status and status.get('health') in ['warning', 'critical']:
                at_risk_targets.append(status)
        
        return at_risk_targets
        
    except Exception as e:
        print(f"Fehler beim Prüfen gefährdeter Ziele: {e}")
        return []
    finally:
        if close_conn and conn:
            conn.close()


def auto_update_target_progress_from_pipeline(
    target_id: int,
    conn: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Aktualisiert den Zielfortschritt automatisch basierend auf Pipeline-Daten.
    
    Args:
        target_id: ID des Ziels
        conn: Optionale Datenbankverbindung
        
    Returns:
        bool: True bei Erfolg
    """
    if not DATABASE_AVAILABLE:
        return False
    
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Lade Ziel-Informationen
        cursor.execute("SELECT period_start, period_end FROM sales_targets WHERE id = ?", (target_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        period_start, period_end = row
        
        # Berechne aktuellen Wert aus gewonnenen Leads
        cursor.execute("""
            SELECT SUM(estimated_value)
            FROM crm_leads
            WHERE stage = 'won'
            AND created_at >= ?
            AND created_at <= ?
        """, (period_start, period_end))
        
        result = cursor.fetchone()
        current_value = result[0] if result[0] else 0
        
        # Aktualisiere Ziel
        return update_target_progress(target_id, current_value, conn)
        
    except Exception as e:
        print(f"Fehler beim automatischen Update des Zielfortschritts: {e}")
        return False
    finally:
        if close_conn and conn:
            conn.close()
