# crm/integration/calculation_bridge.py
"""
Brücke zwischen Berechnungsmodul und CRM-System.
Verknüpft Berechnungsergebnisse mit Kundenprojekten.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any

try:
    from database import get_db_connection, ensure_project_calculations_table
except ImportError:
    def get_db_connection():
        return None
    def ensure_project_calculations_table():
        pass


def save_calculation_to_project(
    project_id: int,
    customer_id: int,
    calculation_data: dict[str, Any],
    calculation_type: str = "pv",
    created_by: str | None = None,
    notes: str | None = None
) -> int | None:
    """
    Speichert Berechnungsergebnisse zu einem Projekt mit automatischer Versionierung.
    
    Args:
        project_id: ID des Projekts
        customer_id: ID des Kunden
        calculation_data: Dictionary mit allen Berechnungsergebnissen
        calculation_type: Typ der Berechnung ('pv', 'heatpump', 'combined')
        created_by: Name des Benutzers (optional)
        notes: Notizen zur Berechnung (optional)
    
    Returns:
        ID der gespeicherten Berechnung oder None bei Fehler
    """
    try:
        conn = get_db_connection()
        if not conn:
            print("Fehler: Keine Datenbankverbindung verfügbar")
            return None
        
        # Stelle sicher, dass die Tabelle existiert
        ensure_project_calculations_table()
        
        cursor = conn.cursor()
        
        # Ermittle die nächste Versionsnummer für dieses Projekt
        cursor.execute(
            """
            SELECT COALESCE(MAX(version), 0) + 1 
            FROM project_calculations 
            WHERE project_id = ?
            """,
            (project_id)
        )
        next_version = cursor.fetchone()[0]
        
        # Konvertiere calculation_data zu JSON
        calculation_json = json.dumps(calculation_data, ensure_ascii=False, indent=2)
        
        # Speichere die Berechnung
        cursor.execute(
            """
            INSERT INTO project_calculations 
            (project_id, customer_id, version, calculation_data, calculation_type, created_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, customer_id, next_version, calculation_json, calculation_type, created_by, notes)
        )
        
        conn.commit()
        calculation_id = cursor.lastrowid
        
        print(f"Berechnung erfolgreich gespeichert: ID={calculation_id}, Version={next_version}")
        
        conn.close()
        return calculation_id
        
    except Exception as e:
        print(f"Fehler beim Speichern der Berechnung: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_calculations_for_project(
    project_id: int,
    include_archived: bool = True
) -> list[dict[str, Any]]:
    """
    Holt alle Berechnungen für ein Projekt.
    
    Args:
        project_id: ID des Projekts
        include_archived: Ob archivierte Berechnungen eingeschlossen werden sollen
    
    Returns:
        Liste von Berechnungs-Dictionaries
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        ensure_project_calculations_table()
        
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id, project_id, customer_id, version, calculation_data, 
                calculation_type, is_main_offer, created_at, created_by, notes
            FROM project_calculations
            WHERE project_id = ?
            ORDER BY version DESC
            """,
            (project_id)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        calculations = []
        for row in rows:
            try:
                calculation_data = json.loads(row[4])
            except json.JSONDecodeError:
                calculation_data = {}
            
            calculations.append({
                'id': row[0],
                'project_id': row[1],
                'customer_id': row[2],
                'version': row[3],
                'calculation_data': calculation_data,
                'calculation_type': row[5],
                'is_main_offer': bool(row[6]),
                'created_at': row[7],
                'created_by': row[8],
                'notes': row[9]
            })
        
        return calculations
        
    except Exception as e:
        print(f"Fehler beim Laden der Berechnungen: {e}")
        return []


def get_calculation_by_id(calculation_id: int) -> dict[str, Any] | None:
    """
    Holt eine spezifische Berechnung anhand ihrer ID.
    
    Args:
        calculation_id: ID der Berechnung
    
    Returns:
        Berechnungs-Dictionary oder None
    """
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        ensure_project_calculations_table()
        
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id, project_id, customer_id, version, calculation_data, 
                calculation_type, is_main_offer, created_at, created_by, notes
            FROM project_calculations
            WHERE id = ?
            """,
            (calculation_id)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        try:
            calculation_data = json.loads(row[4])
        except json.JSONDecodeError:
            calculation_data = {}
        
        return {
            'id': row[0],
            'project_id': row[1],
            'customer_id': row[2],
            'version': row[3],
            'calculation_data': calculation_data,
            'calculation_type': row[5],
            'is_main_offer': bool(row[6]),
            'created_at': row[7],
            'created_by': row[8],
            'notes': row[9]
        }
        
    except Exception as e:
        print(f"Fehler beim Laden der Berechnung: {e}")
        return None


def set_main_offer(calculation_id: int, project_id: int) -> bool:
    """
    Markiert eine Berechnung als Hauptangebot und entfernt die Markierung von allen anderen.
    
    Args:
        calculation_id: ID der Berechnung, die als Hauptangebot markiert werden soll
        project_id: ID des Projekts (zur Sicherheit)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        ensure_project_calculations_table()
        
        cursor = conn.cursor()
        
        # Entferne Hauptangebot-Markierung von allen Berechnungen des Projekts
        cursor.execute(
            """
            UPDATE project_calculations 
            SET is_main_offer = 0 
            WHERE project_id = ?
            """,
            (project_id)
        )
        
        # Setze neue Hauptangebot-Markierung
        cursor.execute(
            """
            UPDATE project_calculations 
            SET is_main_offer = 1 
            WHERE id = ? AND project_id = ?
            """,
            (calculation_id, project_id)
        )
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        if success:
            print(f"Berechnung {calculation_id} als Hauptangebot markiert")
        
        return success
        
    except Exception as e:
        print(f"Fehler beim Setzen des Hauptangebots: {e}")
        return False


def get_main_offer(project_id: int) -> dict[str, Any] | None:
    """
    Holt das als Hauptangebot markierte Berechnungsergebnis für ein Projekt.
    
    Args:
        project_id: ID des Projekts
    
    Returns:
        Berechnungs-Dictionary oder None
    """
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        ensure_project_calculations_table()
        
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                id, project_id, customer_id, version, calculation_data, 
                calculation_type, is_main_offer, created_at, created_by, notes
            FROM project_calculations
            WHERE project_id = ? AND is_main_offer = 1
            LIMIT 1
            """,
            (project_id)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        try:
            calculation_data = json.loads(row[4])
        except json.JSONDecodeError:
            calculation_data = {}
        
        return {
            'id': row[0],
            'project_id': row[1],
            'customer_id': row[2],
            'version': row[3],
            'calculation_data': calculation_data,
            'calculation_type': row[5],
            'is_main_offer': bool(row[6]),
            'created_at': row[7],
            'created_by': row[8],
            'notes': row[9]
        }
        
    except Exception as e:
        print(f"Fehler beim Laden des Hauptangebots: {e}")
        return None


def delete_calculation(calculation_id: int) -> bool:
    """
    Löscht eine Berechnung.
    
    Args:
        calculation_id: ID der zu löschenden Berechnung
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        ensure_project_calculations_table()
        
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM project_calculations WHERE id = ?",
            (calculation_id)
        )
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        if success:
            print(f"Berechnung {calculation_id} gelöscht")
        
        return success
        
    except Exception as e:
        print(f"Fehler beim Löschen der Berechnung: {e}")
        return False


def compare_calculations(calc_id_1: int, calc_id_2: int) -> dict[str, Any]:
    """
    Vergleicht zwei Berechnungen und gibt die Unterschiede zurück.
    
    Args:
        calc_id_1: ID der ersten Berechnung
        calc_id_2: ID der zweiten Berechnung
    
    Returns:
        Dictionary mit Vergleichsdaten
    """
    calc1 = get_calculation_by_id(calc_id_1)
    calc2 = get_calculation_by_id(calc_id_2)
    
    if not calc1 or not calc2:
        return {'error': 'Eine oder beide Berechnungen nicht gefunden'}
    
    # Wichtige Vergleichsfelder
    comparison_fields = [
        'annual_pv_production_kwh',
        'total_investment_netto',
        'total_investment_brutto',
        'annual_total_savings_euro',
        'self_supply_rate_percent',
        'eigenverbrauch_pro_jahr_kwh',
        'netzeinspeisung_kwh',
        'payback_period_years'
    ]
    
    comparison = {
        'calc1': {
            'id': calc1['id'],
            'version': calc1['version'],
            'created_at': calc1['created_at'],
            'values': {}
        },
        'calc2': {
            'id': calc2['id'],
            'version': calc2['version'],
            'created_at': calc2['created_at'],
            'values': {}
        },
        'differences': {}
    }
    
    data1 = calc1['calculation_data']
    data2 = calc2['calculation_data']
    
    for field in comparison_fields:
        val1 = data1.get(field, 0)
        val2 = data2.get(field, 0)
        
        comparison['calc1']['values'][field] = val1
        comparison['calc2']['values'][field] = val2
        
        if val1 != val2:
            try:
                diff = val2 - val1
                diff_percent = (diff / val1 * 100) if val1 != 0 else 0
                comparison['differences'][field] = {
                    'absolute': diff,
                    'percent': diff_percent
                }
            except (TypeError, ZeroDivisionError):
                comparison['differences'][field] = {
                    'absolute': 'N/A',
                    'percent': 'N/A'
                }
    
    return comparison
