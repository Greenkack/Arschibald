"""
PV-Unterkonstruktions-Datenbank
================================

Datenbank-Backend für PV-Montagekomponenten mit CRUD-Operationen,
CSV/XLSX Import und dynamischen Berechnungen.

Autor: Bokuk2 System
Version: 1.0.0
Datum: 2025-11-06
"""

import sqlite3
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from pathlib import Path
import io


# ==================== Datenbankverbindung ====================

DB_PATH = Path(__file__).parent / "data" / "pv_mounting_components.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Erstellt und gibt eine Datenbankverbindung zurück.
    
    Returns:
        sqlite3.Connection: Datenbankverbindung
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    """
    Initialisiert die Datenbank mit allen benötigten Tabellen.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Haupttabelle für Komponenten
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mounting_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            product_name TEXT NOT NULL,
            article_number TEXT,
            category TEXT NOT NULL,
            roof_type TEXT NOT NULL,
            material TEXT,
            dimensions TEXT,
            weight_kg REAL,
            price_netto REAL NOT NULL,
            unit TEXT DEFAULT 'Stk',
            quantity_per_module REAL DEFAULT 1.0,
            compatibility TEXT,
            warranty_years INTEGER,
            specifications TEXT,
            notes TEXT,
            pdf_bytes BLOB,
            pdf_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # Index für schnellere Suche
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_manufacturer 
        ON mounting_components(manufacturer)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_category 
        ON mounting_components(category)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_roof_type 
        ON mounting_components(roof_type)
    """)
    
    # Tabelle für Konfigurationen (komplette Systeme)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_name TEXT NOT NULL,
            roof_type TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            module_count INTEGER NOT NULL,
            components_json TEXT NOT NULL,
            total_price_netto REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


# ==================== CRUD-Operationen ====================

def create_component(component_data: Dict[str, Any]) -> int:
    """
    Erstellt eine neue Komponente in der Datenbank.
    
    Args:
        component_data: Dictionary mit Komponentendaten
        
    Returns:
        int: ID der erstellten Komponente
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # PDF-Bytes separat behandeln
    pdf_bytes = component_data.pop('pdf_bytes', None)
    pdf_filename = component_data.pop('pdf_filename', None)
    
    # Specifications als JSON speichern
    if 'specifications' in component_data and isinstance(component_data['specifications'], dict):
        component_data['specifications'] = json.dumps(component_data['specifications'], ensure_ascii=False)
    
    columns = ', '.join(component_data.keys())
    placeholders = ', '.join(['?' for _ in component_data])
    
    # PDF-Felder hinzufügen falls vorhanden
    if pdf_bytes:
        columns += ', pdf_bytes, pdf_filename'
        placeholders += ', ?, ?'
        values = list(component_data.values()) + [pdf_bytes, pdf_filename]
    else:
        values = list(component_data.values())
    
    query = f"INSERT INTO mounting_components ({columns}) VALUES ({placeholders})"
    
    cursor.execute(query, values)
    component_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return component_id


def read_components(
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    order_by: str = "manufacturer, category"
) -> List[Dict[str, Any]]:
    """
    Liest Komponenten aus der Datenbank mit optionalen Filtern.
    
    Args:
        filters: Dictionary mit Filterkriterien (z.B. {'manufacturer': 'K2 Systems'})
        limit: Maximale Anzahl Ergebnisse
        offset: Offset für Paginierung
        order_by: Sortierung
        
    Returns:
        List[Dict]: Liste mit Komponentendaten
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM mounting_components WHERE is_active = 1"
    params = []
    
    if filters:
        for key, value in filters.items():
            if value is not None:
                if isinstance(value, str) and '%' in value:
                    query += f" AND {key} LIKE ?"
                    params.append(value)
                else:
                    query += f" AND {key} = ?"
                    params.append(value)
    
    query += f" ORDER BY {order_by}"
    
    if limit:
        query += f" LIMIT {limit} OFFSET {offset}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    components = []
    for row in rows:
        component = dict(row)
        # JSON-Felder parsen
        if component.get('specifications'):
            try:
                component['specifications'] = json.loads(component['specifications'])
            except:
                pass
        components.append(component)
    
    conn.close()
    return components


def read_component_by_id(component_id: int, include_pdf: bool = False) -> Optional[Dict[str, Any]]:
    """
    Liest eine einzelne Komponente anhand ihrer ID.
    
    Args:
        component_id: ID der Komponente
        include_pdf: PDF-Bytes einschließen (für Download)
        
    Returns:
        Optional[Dict]: Komponentendaten oder None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if include_pdf:
        cursor.execute("SELECT * FROM mounting_components WHERE id = ?", (component_id))
    else:
        # PDF-Bytes ausschließen für Performance
        cursor.execute("""
            SELECT id, manufacturer, product_name, article_number, category, 
                   roof_type, material, dimensions, weight_kg, price_netto, unit,
                   quantity_per_module, compatibility, warranty_years, specifications,
                   notes, pdf_filename, created_at, updated_at, is_active
            FROM mounting_components WHERE id = ?
        """, (component_id))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        component = dict(row)
        if component.get('specifications'):
            try:
                component['specifications'] = json.loads(component['specifications'])
            except:
                pass
        return component
    return None


def update_component(component_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Aktualisiert eine existierende Komponente.
    
    Args:
        component_id: ID der zu aktualisierenden Komponente
        update_data: Dictionary mit zu aktualisierenden Feldern
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Specifications als JSON speichern
    if 'specifications' in update_data and isinstance(update_data['specifications'], dict):
        update_data['specifications'] = json.dumps(update_data['specifications'], ensure_ascii=False)
    
    # updated_at aktualisieren
    update_data['updated_at'] = datetime.now().isoformat()
    
    set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
    values = list(update_data.values()) + [component_id]
    
    query = f"UPDATE mounting_components SET {set_clause} WHERE id = ?"
    
    cursor.execute(query, values)
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success


def delete_component(component_id: int, soft_delete: bool = True) -> bool:
    """
    Löscht eine Komponente (soft oder hard delete).
    
    Args:
        component_id: ID der zu löschenden Komponente
        soft_delete: True für Soft-Delete (is_active=0), False für Hard-Delete
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if soft_delete:
        cursor.execute(
            "UPDATE mounting_components SET is_active = 0, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), component_id)
        )
    else:
        cursor.execute("DELETE FROM mounting_components WHERE id = ?", (component_id))
    
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success


# ==================== Bulk-Import ====================

def import_from_csv(csv_path: str, encoding: str = 'utf-8') -> Tuple[int, List[str]]:
    """
    Importiert Komponenten aus CSV-Datei.
    
    Args:
        csv_path: Pfad zur CSV-Datei
        encoding: Encoding der CSV-Datei
        
    Returns:
        Tuple[int, List[str]]: (Anzahl importiert, Liste mit Fehlern)
    """
    errors = []
    imported_count = 0
    
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        
        # Erforderliche Felder prüfen
        required_fields = ['manufacturer', 'product_name', 'category', 'roof_type', 'price_netto']
        missing_fields = [f for f in required_fields if f not in df.columns]
        
        if missing_fields:
            errors.append(f"Fehlende Pflichtfelder: {', '.join(missing_fields)}")
            return 0, errors
        
        for idx, row in df.iterrows():
            try:
                component_data = row.to_dict()
                
                # NaN-Werte entfernen
                component_data = {k: v for k, v in component_data.items() if pd.notna(v)}
                
                create_component(component_data)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Fehler beim Lesen der CSV: {str(e)}")
    
    return imported_count, errors


def import_from_excel(excel_path: str, sheet_name: Union[str, int] = 0) -> Tuple[int, List[str]]:
    """
    Importiert Komponenten aus Excel-Datei.
    
    Args:
        excel_path: Pfad zur Excel-Datei
        sheet_name: Name oder Index des Sheets
        
    Returns:
        Tuple[int, List[str]]: (Anzahl importiert, Liste mit Fehlern)
    """
    errors = []
    imported_count = 0
    
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # Erforderliche Felder prüfen
        required_fields = ['manufacturer', 'product_name', 'category', 'roof_type', 'price_netto']
        missing_fields = [f for f in required_fields if f not in df.columns]
        
        if missing_fields:
            errors.append(f"Fehlende Pflichtfelder: {', '.join(missing_fields)}")
            return 0, errors
        
        for idx, row in df.iterrows():
            try:
                component_data = row.to_dict()
                
                # NaN-Werte entfernen
                component_data = {k: v for k, v in component_data.items() if pd.notna(v)}
                
                create_component(component_data)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Zeile {idx + 2}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Fehler beim Lesen der Excel-Datei: {str(e)}")
    
    return imported_count, errors


# ==================== Export ====================

def export_to_csv(output_path: str, filters: Optional[Dict[str, Any]] = None) -> bool:
    """
    Exportiert Komponenten als CSV.
    
    Args:
        output_path: Ziel-Pfad für CSV-Datei
        filters: Optionale Filter
        
    Returns:
        bool: True bei Erfolg
    """
    try:
        components = read_components(filters=filters)
        
        # PDF-Bytes entfernen für CSV
        for comp in components:
            comp.pop('pdf_bytes', None)
            if isinstance(comp.get('specifications'), dict):
                comp['specifications'] = json.dumps(comp['specifications'], ensure_ascii=False)
        
        df = pd.DataFrame(components)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return True
        
    except Exception as e:
        print(f"Export-Fehler: {e}")
        return False


def export_to_excel(output_path: str, filters: Optional[Dict[str, Any]] = None) -> bool:
    """
    Exportiert Komponenten als Excel.
    
    Args:
        output_path: Ziel-Pfad für Excel-Datei
        filters: Optionale Filter
        
    Returns:
        bool: True bei Erfolg
    """
    try:
        components = read_components(filters=filters)
        
        # PDF-Bytes entfernen für Excel
        for comp in components:
            comp.pop('pdf_bytes', None)
            if isinstance(comp.get('specifications'), dict):
                comp['specifications'] = json.dumps(comp['specifications'], ensure_ascii=False)
        
        df = pd.DataFrame(components)
        df.to_excel(output_path, index=False, sheet_name='PV-Komponenten')
        return True
        
    except Exception as e:
        print(f"Export-Fehler: {e}")
        return False


# ==================== Statistiken ====================

def get_statistics() -> Dict[str, Any]:
    """
    Gibt Statistiken über die Datenbank zurück.
    
    Returns:
        Dict: Statistiken (Anzahl Komponenten, Hersteller, etc.)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Gesamtanzahl
    cursor.execute("SELECT COUNT(*) as count FROM mounting_components WHERE is_active = 1")
    stats['total_components'] = cursor.fetchone()['count']
    
    # Nach Hersteller
    cursor.execute("""
        SELECT manufacturer, COUNT(*) as count 
        FROM mounting_components 
        WHERE is_active = 1 
        GROUP BY manufacturer
        ORDER BY count DESC
    """)
    stats['by_manufacturer'] = {row['manufacturer']: row['count'] for row in cursor.fetchall()}
    
    # Nach Kategorie
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM mounting_components 
        WHERE is_active = 1 
        GROUP BY category
        ORDER BY count DESC
    """)
    stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}
    
    # Nach Dachtyp
    cursor.execute("""
        SELECT roof_type, COUNT(*) as count 
        FROM mounting_components 
        WHERE is_active = 1 
        GROUP BY roof_type
        ORDER BY count DESC
    """)
    stats['by_roof_type'] = {row['roof_type']: row['count'] for row in cursor.fetchall()}
    
    # Preisstatistiken
    cursor.execute("""
        SELECT 
            MIN(price_netto) as min_price,
            MAX(price_netto) as max_price,
            AVG(price_netto) as avg_price
        FROM mounting_components 
        WHERE is_active = 1
    """)
    price_stats = dict(cursor.fetchone())
    stats['price_statistics'] = price_stats
    
    conn.close()
    return stats


# ==================== Suchfunktionen ====================

def search_components(
    search_term: str,
    search_fields: List[str] = ['product_name', 'manufacturer', 'article_number', 'notes']
) -> List[Dict[str, Any]]:
    """
    Volltextsuche in Komponenten.
    
    Args:
        search_term: Suchbegriff
        search_fields: Felder, in denen gesucht werden soll
        
    Returns:
        List[Dict]: Gefundene Komponenten
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    for field in search_fields:
        where_clauses.append(f"{field} LIKE ?")
        params.append(f"%{search_term}%")
    
    query = f"""
        SELECT * FROM mounting_components 
        WHERE is_active = 1 AND ({' OR '.join(where_clauses)})
        ORDER BY manufacturer, category
    """
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    components = []
    for row in rows:
        component = dict(row)
        # PDF-Bytes ausschließen
        component.pop('pdf_bytes', None)
        if component.get('specifications'):
            try:
                component['specifications'] = json.loads(component['specifications'])
            except:
                pass
        components.append(component)
    
    conn.close()
    return components


# ==================== Initialisierung ====================

# Datenbank beim Import initialisieren
initialize_database()
