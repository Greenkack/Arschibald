# crm/utils/import_export_manager.py
"""
Kunden Import/Export Manager

Ermöglicht den Import und Export von Kundendaten in verschiedenen Formaten:
- CSV Import/Export
- Excel Import/Export
- Duplikatserkennung
- Datenvalidierung

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

import csv
import io
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd


# ============================================================================
# FIELD MAPPING
# ============================================================================

# Alle Kundenfelder mit deutschen Beschreibungen
CUSTOMER_FIELDS = {
    'id': 'ID',
    'salutation': 'Anrede',
    'title': 'Titel',
    'first_name': 'Vorname',
    'last_name': 'Nachname',
    'company_name': 'Firmenname',
    'address': 'Straße',
    'house_number': 'Hausnummer',
    'zip_code': 'PLZ',
    'city': 'Stadt',
    'state': 'Bundesland',
    'region': 'Region',
    'email': 'E-Mail',
    'phone_landline': 'Telefon (Festnetz)',
    'phone_mobile': 'Telefon (Mobil)',
    'income_tax_rate_percent': 'Einkommensteuersatz (%)',
    'creation_date': 'Erstellungsdatum',
    'last_updated': 'Letzte Aktualisierung'
}

# Pflichtfelder für Import
REQUIRED_FIELDS = ['first_name', 'last_name']

# Felder für Duplikatserkennung
DUPLICATE_CHECK_FIELDS = ['email', 'phone_mobile', 'phone_landline']


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_customers_to_csv(
    conn: sqlite3.Connection,
    include_fields: Optional[List[str]] = None,
    customer_ids: Optional[List[int]] = None
) -> str:
    """
    Exportiert Kundendaten als CSV-String.
    
    Args:
        conn: Datenbankverbindung
        include_fields: Liste der zu exportierenden Felder (None = alle)
        customer_ids: Liste der zu exportierenden Kunden-IDs (None = alle)
    
    Returns:
        CSV-String mit Kundendaten
    """
    try:
        cursor = conn.cursor()
        
        # Felder bestimmen
        if include_fields is None:
            include_fields = list(CUSTOMER_FIELDS.keys())
        
        # SQL Query erstellen
        fields_str = ', '.join(include_fields)
        query = f"SELECT {fields_str} FROM customers"
        
        if customer_ids:
            placeholders = ','.join('?' * len(customer_ids))
            query += f" WHERE id IN ({placeholders})"
            cursor.execute(query, customer_ids)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        
        # CSV erstellen
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header mit deutschen Beschreibungen
        header = [CUSTOMER_FIELDS.get(field, field) for field in include_fields]
        writer.writerow(header)
        
        # Daten
        for row in rows:
            writer.writerow(row)
        
        return output.getvalue()
        
    except Exception as e:
        print(f"Fehler beim CSV-Export: {e}")
        return ""


def export_customers_to_excel(
    conn: sqlite3.Connection,
    filepath: str,
    include_fields: Optional[List[str]] = None,
    customer_ids: Optional[List[int]] = None
) -> bool:
    """
    Exportiert Kundendaten als Excel-Datei.
    
    Args:
        conn: Datenbankverbindung
        filepath: Pfad zur Excel-Datei
        include_fields: Liste der zu exportierenden Felder (None = alle)
        customer_ids: Liste der zu exportierenden Kunden-IDs (None = alle)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        cursor = conn.cursor()
        
        # Felder bestimmen
        if include_fields is None:
            include_fields = list(CUSTOMER_FIELDS.keys())
        
        # SQL Query erstellen
        fields_str = ', '.join(include_fields)
        query = f"SELECT {fields_str} FROM customers"
        
        if customer_ids:
            placeholders = ','.join('?' * len(customer_ids))
            query += f" WHERE id IN ({placeholders})"
            cursor.execute(query, customer_ids)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        
        # DataFrame erstellen
        df = pd.DataFrame(rows, columns=include_fields)
        
        # Spaltennamen auf Deutsch
        df.columns = [CUSTOMER_FIELDS.get(field, field) for field in include_fields]
        
        # Excel schreiben
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return True
        
    except Exception as e:
        print(f"Fehler beim Excel-Export: {e}")
        return False


def get_export_statistics(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Gibt Statistiken über exportierbare Daten zurück.
    
    Args:
        conn: Datenbankverbindung
    
    Returns:
        Dictionary mit Statistiken
    """
    try:
        cursor = conn.cursor()
        
        # Gesamtanzahl Kunden
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        # Kunden mit E-Mail
        cursor.execute("SELECT COUNT(*) FROM customers WHERE email IS NOT NULL AND email != ''")
        customers_with_email = cursor.fetchone()[0]
        
        # Kunden mit Telefon
        cursor.execute("""
            SELECT COUNT(*) FROM customers 
            WHERE (phone_mobile IS NOT NULL AND phone_mobile != '') 
               OR (phone_landline IS NOT NULL AND phone_landline != '')
        """)
        customers_with_phone = cursor.fetchone()[0]
        
        # Kunden mit Firma
        cursor.execute("SELECT COUNT(*) FROM customers WHERE company_name IS NOT NULL AND company_name != ''")
        customers_with_company = cursor.fetchone()[0]
        
        return {
            'total_customers': total_customers,
            'customers_with_email': customers_with_email,
            'customers_with_phone': customers_with_phone,
            'customers_with_company': customers_with_company,
            'completeness_rate': round((customers_with_email / total_customers * 100) if total_customers > 0 else 0, 1)
        }
        
    except Exception as e:
        print(f"Fehler beim Abrufen der Export-Statistiken: {e}")
        return {}


# ============================================================================
# IMPORT FUNCTIONS
# ============================================================================

def parse_csv_for_import(
    csv_content: str,
    delimiter: str = ',',
    encoding: str = 'utf-8'
) -> Tuple[List[str], List[List[str]], List[str]]:
    """
    Parst CSV-Inhalt und gibt Header, Daten und Fehler zurück.
    
    Args:
        csv_content: CSV-Inhalt als String
        delimiter: CSV-Trennzeichen
        encoding: Zeichenkodierung
    
    Returns:
        Tuple: (header, rows, errors)
    """
    errors = []
    
    try:
        # CSV parsen
        csv_file = io.StringIO(csv_content)
        reader = csv.reader(csv_file, delimiter=delimiter)
        
        # Header lesen
        header = next(reader, None)
        if not header:
            errors.append("CSV-Datei enthält keinen Header")
            return [], [], errors
        
        # Daten lesen
        rows = list(reader)
        
        if not rows:
            errors.append("CSV-Datei enthält keine Daten")
            return header, [], errors
        
        return header, rows, errors
        
    except Exception as e:
        errors.append(f"Fehler beim Parsen der CSV-Datei: {str(e)}")
        return [], [], errors


def parse_excel_for_import(
    filepath: str,
    sheet_name: Optional[str] = None
) -> Tuple[List[str], List[List[Any]], List[str]]:
    """
    Parst Excel-Datei und gibt Header, Daten und Fehler zurück.
    
    Args:
        filepath: Pfad zur Excel-Datei
        sheet_name: Name des Sheets (None = erstes Sheet)
    
    Returns:
        Tuple: (header, rows, errors)
    """
    errors = []
    
    try:
        # Excel lesen
        if sheet_name:
            df = pd.read_excel(filepath, sheet_name=sheet_name, engine='openpyxl')
        else:
            df = pd.read_excel(filepath, engine='openpyxl')
        
        # Header
        header = df.columns.tolist()
        
        # Daten (NaN durch None ersetzen)
        rows = df.fillna('').values.tolist()
        
        if not rows:
            errors.append("Excel-Datei enthält keine Daten")
            return header, [], errors
        
        return header, rows, errors
        
    except Exception as e:
        errors.append(f"Fehler beim Lesen der Excel-Datei: {str(e)}")
        return [], [], errors


def get_excel_sheet_names(filepath: str) -> List[str]:
    """
    Gibt alle Sheet-Namen einer Excel-Datei zurück.
    
    Args:
        filepath: Pfad zur Excel-Datei
    
    Returns:
        Liste der Sheet-Namen
    """
    try:
        excel_file = pd.ExcelFile(filepath, engine='openpyxl')
        return excel_file.sheet_names
    except Exception as e:
        print(f"Fehler beim Lesen der Sheet-Namen: {e}")
        return []


def map_import_fields(
    import_header: List[str],
    field_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Erstellt Mapping zwischen Import-Spalten und Datenbankfeldern.
    
    Args:
        import_header: Header aus Import-Datei
        field_mapping: Optionales manuelles Mapping
    
    Returns:
        Dictionary: {import_column: db_field}
    """
    mapping = {}
    
    if field_mapping:
        # Manuelles Mapping verwenden
        mapping = field_mapping.copy()
    else:
        # Automatisches Mapping versuchen
        # Normalisiere Header (lowercase, ohne Sonderzeichen)
        for import_col in import_header:
            import_col_normalized = import_col.lower().strip()
            
            # Direkte Übereinstimmung mit deutschen Beschreibungen
            for db_field, german_name in CUSTOMER_FIELDS.items():
                if import_col_normalized == german_name.lower():
                    mapping[import_col] = db_field
                    break
            
            # Übereinstimmung mit englischen Feldnamen
            if import_col not in mapping:
                for db_field in CUSTOMER_FIELDS.keys():
                    if import_col_normalized == db_field.lower():
                        mapping[import_col] = db_field
                        break
            
            # Teilübereinstimmungen
            if import_col not in mapping:
                if 'vorname' in import_col_normalized or 'first' in import_col_normalized:
                    mapping[import_col] = 'first_name'
                elif 'nachname' in import_col_normalized or 'last' in import_col_normalized:
                    mapping[import_col] = 'last_name'
                elif 'mail' in import_col_normalized:
                    mapping[import_col] = 'email'
                elif 'firma' in import_col_normalized or 'company' in import_col_normalized:
                    mapping[import_col] = 'company_name'
                elif 'plz' in import_col_normalized or 'zip' in import_col_normalized:
                    mapping[import_col] = 'zip_code'
                elif 'stadt' in import_col_normalized or 'city' in import_col_normalized:
                    mapping[import_col] = 'city'
                elif 'straße' in import_col_normalized or 'strasse' in import_col_normalized or 'street' in import_col_normalized or 'address' in import_col_normalized:
                    mapping[import_col] = 'address'
                elif 'mobil' in import_col_normalized or 'handy' in import_col_normalized or 'mobile' in import_col_normalized:
                    mapping[import_col] = 'phone_mobile'
                elif 'telefon' in import_col_normalized or 'phone' in import_col_normalized or 'festnetz' in import_col_normalized:
                    mapping[import_col] = 'phone_landline'
    
    return mapping


def check_duplicate_customer(
    conn: sqlite3.Connection,
    customer_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Prüft, ob ein Kunde bereits existiert (basierend auf E-Mail oder Telefon).
    
    Args:
        conn: Datenbankverbindung
        customer_data: Kundendaten zum Prüfen
    
    Returns:
        Existierender Kunde als Dictionary oder None
    """
    try:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        
        # Prüfe E-Mail
        if customer_data.get('email'):
            cursor.execute(
                "SELECT * FROM customers WHERE email = ? AND email != ''",
                (customer_data['email'],)
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
        
        # Prüfe Mobiltelefon
        if customer_data.get('phone_mobile'):
            cursor.execute(
                "SELECT * FROM customers WHERE phone_mobile = ? AND phone_mobile != ''",
                (customer_data['phone_mobile'],)
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
        
        # Prüfe Festnetz
        if customer_data.get('phone_landline'):
            cursor.execute(
                "SELECT * FROM customers WHERE phone_landline = ? AND phone_landline != ''",
                (customer_data['phone_landline'],)
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
        
        # Prüfe Name + PLZ (schwächere Duplikatserkennung)
        if customer_data.get('first_name') and customer_data.get('last_name') and customer_data.get('zip_code'):
            cursor.execute(
                """SELECT * FROM customers 
                   WHERE first_name = ? AND last_name = ? AND zip_code = ?""",
                (customer_data['first_name'], customer_data['last_name'], customer_data['zip_code'])
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
        
        return None
        
    except Exception as e:
        print(f"Fehler bei Duplikatsprüfung: {e}")
        return None


def validate_customer_data(customer_data: Dict[str, Any]) -> List[str]:
    """
    Validiert Kundendaten vor dem Import.
    
    Args:
        customer_data: Zu validierende Kundendaten
    
    Returns:
        Liste von Fehlermeldungen (leer = valide)
    """
    errors = []
    
    # Pflichtfelder prüfen
    for field in REQUIRED_FIELDS:
        if not customer_data.get(field):
            field_name = CUSTOMER_FIELDS.get(field, field)
            errors.append(f"Pflichtfeld fehlt: {field_name}")
    
    # E-Mail-Format prüfen (einfache Validierung)
    if customer_data.get('email'):
        email = customer_data['email']
        if '@' not in email or '.' not in email:
            errors.append(f"Ungültiges E-Mail-Format: {email}")
    
    # PLZ prüfen (sollte numerisch sein)
    if customer_data.get('zip_code'):
        zip_code = str(customer_data['zip_code']).strip()
        if not zip_code.isdigit() or len(zip_code) != 5:
            errors.append(f"Ungültige PLZ: {zip_code} (muss 5-stellig sein)")
    
    # Steuersatz prüfen
    if customer_data.get('income_tax_rate_percent'):
        try:
            rate = float(customer_data['income_tax_rate_percent'])
            if rate < 0 or rate > 100:
                errors.append(f"Ungültiger Steuersatz: {rate}% (muss zwischen 0 und 100 liegen)")
        except (ValueError, TypeError):
            errors.append(f"Ungültiger Steuersatz: {customer_data['income_tax_rate_percent']}")
    
    return errors


def import_customer(
    conn: sqlite3.Connection,
    customer_data: Dict[str, Any],
    duplicate_action: str = 'skip'
) -> Tuple[bool, Optional[int], str]:
    """
    Importiert einen einzelnen Kunden.
    
    Args:
        conn: Datenbankverbindung
        customer_data: Kundendaten
        duplicate_action: Aktion bei Duplikat ('skip', 'update', 'create')
    
    Returns:
        Tuple: (success, customer_id, message)
    """
    try:
        # Validierung
        validation_errors = validate_customer_data(customer_data)
        if validation_errors:
            return False, None, "; ".join(validation_errors)
        
        # Duplikatsprüfung
        existing_customer = check_duplicate_customer(conn, customer_data)
        
        if existing_customer:
            if duplicate_action == 'skip':
                return False, existing_customer['id'], f"Kunde existiert bereits (ID: {existing_customer['id']})"
            elif duplicate_action == 'update':
                # Kunde aktualisieren
                return update_customer_from_import(conn, existing_customer['id'], customer_data)
            # Bei 'create' wird trotz Duplikat ein neuer Kunde erstellt
        
        # Neuen Kunden erstellen
        cursor = conn.cursor()
        
        # Zeitstempel
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        customer_data['creation_date'] = now
        customer_data['last_updated'] = now
        
        # SQL erstellen
        fields = [k for k in customer_data.keys() if k in CUSTOMER_FIELDS]
        placeholders = ','.join(['?' for _ in fields])
        fields_str = ','.join(fields)
        
        query = f"INSERT INTO customers ({fields_str}) VALUES ({placeholders})"
        values = [customer_data.get(f) for f in fields]
        
        cursor.execute(query, values)
        conn.commit()
        
        customer_id = cursor.lastrowid
        return True, customer_id, f"Kunde erfolgreich importiert (ID: {customer_id})"
        
    except Exception as e:
        return False, None, f"Fehler beim Import: {str(e)}"


def update_customer_from_import(
    conn: sqlite3.Connection,
    customer_id: int,
    customer_data: Dict[str, Any]
) -> Tuple[bool, int, str]:
    """
    Aktualisiert einen existierenden Kunden mit Import-Daten.
    
    Args:
        conn: Datenbankverbindung
        customer_id: ID des zu aktualisierenden Kunden
        customer_data: Neue Kundendaten
    
    Returns:
        Tuple: (success, customer_id, message)
    """
    try:
        cursor = conn.cursor()
        
        # Zeitstempel
        customer_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # SQL erstellen (nur Felder aktualisieren, die vorhanden sind)
        update_fields = [k for k in customer_data.keys() if k in CUSTOMER_FIELDS and k != 'id']
        set_clause = ','.join([f"{field} = ?" for field in update_fields])
        
        query = f"UPDATE customers SET {set_clause} WHERE id = ?"
        values = [customer_data.get(f) for f in update_fields] + [customer_id]
        
        cursor.execute(query, values)
        conn.commit()
        
        return True, customer_id, f"Kunde erfolgreich aktualisiert (ID: {customer_id})"
        
    except Exception as e:
        return False, customer_id, f"Fehler beim Aktualisieren: {str(e)}"


def import_customers_batch(
    conn: sqlite3.Connection,
    rows: List[List[Any]],
    field_mapping: Dict[str, str],
    duplicate_action: str = 'skip'
) -> Dict[str, Any]:
    """
    Importiert mehrere Kunden auf einmal.
    
    Args:
        conn: Datenbankverbindung
        rows: Liste von Datenzeilen
        field_mapping: Mapping zwischen Import-Spalten und DB-Feldern
        duplicate_action: Aktion bei Duplikat ('skip', 'update', 'create')
    
    Returns:
        Dictionary mit Import-Statistiken
    """
    stats = {
        'total': len(rows),
        'success': 0,
        'skipped': 0,
        'updated': 0,
        'errors': 0,
        'error_details': []
    }
    
    # Reverse mapping für Spaltenindex
    import_columns = list(field_mapping.keys())
    
    for row_idx, row in enumerate(rows, start=2):  # Start bei 2 (Header ist Zeile 1)
        try:
            # Kundendaten aus Zeile extrahieren
            customer_data = {}
            for col_idx, import_col in enumerate(import_columns):
                if col_idx < len(row):
                    db_field = field_mapping.get(import_col)
                    if db_field:
                        value = row[col_idx]
                        # Leere Strings als None behandeln
                        customer_data[db_field] = value if value != '' else None
            
            # Import durchführen
            success, customer_id, message = import_customer(conn, customer_data, duplicate_action)
            
            if success:
                if 'aktualisiert' in message:
                    stats['updated'] += 1
                else:
                    stats['success'] += 1
            else:
                if 'existiert bereits' in message:
                    stats['skipped'] += 1
                else:
                    stats['errors'] += 1
                    stats['error_details'].append(f"Zeile {row_idx}: {message}")
        
        except Exception as e:
            stats['errors'] += 1
            stats['error_details'].append(f"Zeile {row_idx}: {str(e)}")
    
    return stats


def preview_import_data(
    rows: List[List[Any]],
    field_mapping: Dict[str, str],
    max_rows: int = 10
) -> List[Dict[str, Any]]:
    """
    Erstellt eine Vorschau der zu importierenden Daten.
    
    Args:
        rows: Datenzeilen
        field_mapping: Feld-Mapping
        max_rows: Maximale Anzahl Zeilen für Vorschau
    
    Returns:
        Liste von Dictionaries mit Vorschaudaten
    """
    preview = []
    import_columns = list(field_mapping.keys())
    
    for row in rows[:max_rows]:
        customer_data = {}
        for col_idx, import_col in enumerate(import_columns):
            if col_idx < len(row):
                db_field = field_mapping.get(import_col)
                if db_field:
                    customer_data[CUSTOMER_FIELDS.get(db_field, db_field)] = row[col_idx]
        
        preview.append(customer_data)
    
    return preview


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_db_fields() -> Dict[str, str]:
    """
    Gibt alle verfügbaren Datenbankfelder mit deutschen Beschreibungen zurück.
    
    Returns:
        Dictionary: {db_field: german_description}
    """
    return CUSTOMER_FIELDS.copy()


def get_required_fields() -> List[str]:
    """
    Gibt Liste der Pflichtfelder zurück.
    
    Returns:
        Liste der Pflichtfelder
    """
    return REQUIRED_FIELDS.copy()


def format_import_statistics(stats: Dict[str, Any]) -> str:
    """
    Formatiert Import-Statistiken als lesbaren Text.
    
    Args:
        stats: Statistik-Dictionary
    
    Returns:
        Formatierter Text
    """
    lines = [
        f"Import abgeschlossen:",
        f"  Gesamt: {stats['total']} Zeilen",
        f"  Erfolgreich importiert: {stats['success']}",
        f"  ↻ Aktualisiert: {stats['updated']}",
        f"  ⊘ Übersprungen (Duplikate): {stats['skipped']}",
        f"  Fehler: {stats['errors']}"
    ]
    
    if stats['error_details']:
        lines.append("\nFehlerdetails:")
        for error in stats['error_details'][:10]:  # Maximal 10 Fehler anzeigen
            lines.append(f"  • {error}")
        
        if len(stats['error_details']) > 10:
            lines.append(f"  ... und {len(stats['error_details']) - 10} weitere Fehler")
    
    return '\n'.join(lines)
