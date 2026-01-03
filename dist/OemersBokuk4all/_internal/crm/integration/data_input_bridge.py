# crm/integration/data_input_bridge.py
"""
Brückenmodul für die automatische Datenübernahme aus der Bedarfsanalyse ins CRM.

Dieses Modul extrahiert Kunden- und Projektdaten aus st.session_state.project_data
und bereitet sie für die Speicherung im CRM vor.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional


def extract_customer_data_from_session() -> Dict[str, Any]:
    """
    Extrahiert alle Kundendaten aus st.session_state.project_data.
    
    Returns:
        Dictionary mit allen Kundenfeldern für CRM-Speicherung
    """
    import streamlit as st
    
    project_data = st.session_state.get("project_data", {})
    customer_data = project_data.get("customer_data", {})
    
    def _clean(value: Any) -> Any:
        """Bereinigt String-Werte (trim whitespace)"""
        if isinstance(value, str):
            return value.strip()
        return value
    
    # Sicherstellen, dass Pflichtfelder vorhanden sind
    first_name = _clean(customer_data.get("first_name", ""))
    last_name = _clean(customer_data.get("last_name", ""))
    company_name = _clean(customer_data.get("company_name", ""))
    
    # Fallback für fehlende Namen
    if not first_name:
        first_name = company_name or "Interessent"
    if not last_name:
        last_name = company_name or "Unbekannt"
    
    # Vollständige Kundenaten extrahieren
    extracted_data = {
        # Pflichtfelder
        'first_name': first_name,
        'last_name': last_name,
        
        # Persönliche Daten
        'salutation': _clean(customer_data.get('salutation', '')),
        'title': _clean(customer_data.get('title', '')),
        'company_name': company_name,
        'num_persons': int(customer_data.get('num_persons', 1) or 1),
        
        # Adressdaten
        'address': _clean(customer_data.get('address', '')),
        'house_number': _clean(customer_data.get('house_number', '')),
        'zip_code': _clean(customer_data.get('zip_code', '')),
        'city': _clean(customer_data.get('city', '')),
        'state': _clean(customer_data.get('state', '')),
        'region': _clean(customer_data.get('region', '')),
        'full_address': _clean(customer_data.get('full_address', '')),
        
        # Kontaktdaten
        'email': _clean(customer_data.get('email', '')),
        'phone_landline': _clean(customer_data.get('phone_landline') or customer_data.get('phone', '')),
        'phone_mobile': _clean(customer_data.get('phone_mobile', '')),
        
        # Finanzielle Daten
        'income_tax_rate_percent': float(customer_data.get('income_tax_rate_percent', 0.0) or 0.0),
        
        # Kundentyp
        'type': _clean(customer_data.get('type', 'Privat')),
        
        # Metadaten
        'creation_date': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
    }
    
    return extracted_data


def extract_project_data_from_session() -> Dict[str, Any]:
    """
    Extrahiert alle Projektdaten aus st.session_state.project_data.
    
    Returns:
        Dictionary mit allen Projektfeldern für CRM-Speicherung
    """
    import streamlit as st
    
    project_data = st.session_state.get("project_data", {})
    project_details = project_data.get("project_details", {})
    consumption_data = project_data.get("consumption_data", {})
    
    def _clean(value: Any) -> Any:
        """Bereinigt String-Werte (trim whitespace)"""
        if isinstance(value, str):
            return value.strip()
        return value
    
    # Projektname generieren falls nicht vorhanden
    project_name = _clean(project_details.get('project_name', ''))
    if not project_name:
        project_name = f"Projekt {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Vollständige Projektdaten extrahieren
    extracted_data = {
        # Basis-Projektdaten
        'project_name': project_name,
        'project_status': _clean(project_details.get('project_status', 'Angebot')),
        
        # Anlagentyp und Einspeisetyp
        'anlage_type': _clean(project_details.get('anlage_type', 'Neuanlage')),
        'feed_in_type': _clean(project_details.get('feed_in_type', 'Teileinspeisung')),
        
        # Dach-Daten
        'roof_type': _clean(project_details.get('roof_type', '')),
        'roof_covering_type': _clean(project_details.get('roof_covering_type', '')),
        'free_roof_area_sqm': project_details.get('free_roof_area_sqm'),
        'roof_orientation': _clean(project_details.get('roof_orientation', '')),
        'roof_inclination_deg': project_details.get('roof_inclination_deg'),
        'building_height_gt_7m': int(bool(project_details.get('building_height_gt_7m', False))),
        
        # Verbrauchs-Daten (aus project_details oder consumption_data)
        'annual_consumption_kwh': (
            project_details.get('annual_consumption_kwh') or 
            consumption_data.get('annual_consumption') or 
            consumption_data.get('consumption_household_kwh_yr')
        ),
        'costs_household_euro_mo': (
            project_details.get('costs_household_euro_mo') or
            consumption_data.get('costs_household_euro_mo')
        ),
        'annual_heating_kwh': (
            project_details.get('annual_heating_kwh') or 
            consumption_data.get('consumption_heating_kwh_yr')
        ),
        'costs_heating_euro_mo': (
            project_details.get('costs_heating_euro_mo') or
            consumption_data.get('costs_heating_euro_mo')
        ),
        
        # PV-Komponenten
        'module_quantity': project_details.get('module_quantity'),
        'selected_module_id': project_details.get('selected_module_id'),
        'selected_inverter_id': project_details.get('selected_inverter_id'),
        
        # Speicher
        'include_storage': int(bool(project_details.get('include_storage', False))),
        'selected_storage_id': project_details.get('selected_storage_id'),
        'selected_storage_storage_power_kw': project_details.get('selected_storage_storage_power_kw'),
        
        # Zusatzkomponenten
        'include_additional_components': int(bool(project_details.get('include_additional_components', False))),
        'selected_wallbox_id': project_details.get('selected_wallbox_id'),
        'selected_ems_id': project_details.get('selected_ems_id'),
        'selected_optimizer_id': project_details.get('selected_optimizer_id'),
        'selected_carport_id': project_details.get('selected_carport_id'),
        'selected_notstrom_id': project_details.get('selected_notstrom_id'),
        'selected_tierabwehr_id': project_details.get('selected_tierabwehr_id'),
        
        # Visualisierung
        'visualize_roof_in_pdf': int(bool(project_details.get('visualize_roof_in_pdf', False))),
        
        # Geo-Koordinaten
        'latitude': project_details.get('latitude'),
        'longitude': project_details.get('longitude'),
        
        # Metadaten
        'creation_date': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
    }
    
    return extracted_data


def check_duplicate_customer(conn: sqlite3.Connection, email: str) -> Optional[Dict[str, Any]]:
    """
    Prüft ob ein Kunde mit der angegebenen E-Mail bereits existiert.
    
    Args:
        conn: SQLite Datenbankverbindung
        email: E-Mail-Adresse zum Prüfen
    
    Returns:
        Dictionary mit Kundendaten falls gefunden, sonst None
    """
    if not email or not email.strip():
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM customers WHERE LOWER(email) = LOWER(?) LIMIT 1",
            (email.strip())
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"Fehler bei Duplikatsprüfung: {e}")
        return None


def validate_required_fields(customer_data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validiert ob alle Pflichtfelder vorhanden sind.
    
    Args:
        customer_data: Dictionary mit Kundendaten
    
    Returns:
        Tuple (is_valid, missing_fields)
        - is_valid: True wenn alle Pflichtfelder vorhanden
        - missing_fields: Liste der fehlenden Felder
    """
    required_fields = {
        'first_name': 'Vorname',
        'last_name': 'Nachname',
    }
    
    missing = []
    for field, label in required_fields.items():
        value = customer_data.get(field, '')
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(label)
    
    return len(missing) == 0, missing


def get_data_preview_summary(customer_data: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Erstellt eine Zusammenfassung der zu übernehmenden Daten für die Vorschau.
    
    Args:
        customer_data: Extrahierte Kundendaten
        project_data: Extrahierte Projektdaten
    
    Returns:
        Dictionary mit strukturierter Zusammenfassung
    """
    summary = {
        'customer': {
            'name': f"{customer_data.get('salutation', '')} {customer_data.get('title', '')} {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
            'company': customer_data.get('company_name', ''),
            'address': f"{customer_data.get('address', '')} {customer_data.get('house_number', '')}, {customer_data.get('zip_code', '')} {customer_data.get('city', '')}".strip(),
            'email': customer_data.get('email', ''),
            'phone': customer_data.get('phone_landline', '') or customer_data.get('phone_mobile', ''),
            'type': customer_data.get('type', 'Privat'),
        },
        'project': {
            'name': project_data.get('project_name', ''),
            'status': project_data.get('project_status', ''),
            'anlage_type': project_data.get('anlage_type', ''),
            'feed_in_type': project_data.get('feed_in_type', ''),
            'roof_type': project_data.get('roof_type', ''),
            'module_quantity': project_data.get('module_quantity', 0),
            'annual_consumption_kwh': project_data.get('annual_consumption_kwh', 0),
            'has_storage': bool(project_data.get('include_storage', False)),
        },
        'counts': {
            'customer_fields': sum(1 for v in customer_data.values() if v and str(v).strip()),
            'project_fields': sum(1 for v in project_data.values() if v and str(v).strip()),
        }
    }
    
    return summary
