"""
CRM Integration: PDF Bridge
Automatische PDF-Archivierung in Kundenakte

Dieses Modul ermöglicht die automatische Speicherung von generierten PDFs
in der Kundenakte mit Metadaten-Extraktion und Versionierung.

Autor: Kiro AI
Datum: 2025-01-13
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def extract_pdf_metadata(
    pdf_path: str,
    offer_data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Extrahiert Metadaten aus PDF-Datei und Angebotsdaten.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        offer_data: Optional - Angebotsdaten für zusätzliche Metadaten
    
    Returns:
        Dictionary mit Metadaten (doc_type, version, date, etc.)
    """
    metadata = {
        'doc_type': 'offer_pdf',
        'version': 1,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'file_size': 0
    }
    
    # Dateigröße ermitteln
    try:
        if os.path.exists(pdf_path):
            metadata['file_size'] = os.path.getsize(pdf_path)
    except Exception as e:
        print(f"PDF Bridge: Fehler beim Ermitteln der Dateigröße: {e}")
    
    # PDF-Typ aus Dateinamen extrahieren
    filename = os.path.basename(pdf_path).lower()
    
    if 'angebot' in filename or 'offer' in filename:
        metadata['doc_type'] = 'offer_pdf'
    elif 'rechnung' in filename or 'invoice' in filename:
        metadata['doc_type'] = 'invoice_pdf'
    elif 'vertrag' in filename or 'contract' in filename:
        metadata['doc_type'] = 'contract_pdf'
    elif 'bericht' in filename or 'report' in filename:
        metadata['doc_type'] = 'report_pdf'
    else:
        metadata['doc_type'] = 'other_pdf'
    
    # Zusätzliche Metadaten aus offer_data
    if offer_data:
        metadata['offer_id'] = offer_data.get('offer_id', '')
        metadata['customer_name'] = offer_data.get('customer', {}).get('name', '')
        metadata['project_type'] = offer_data.get('project_type', 'pv')
    
    return metadata


def get_next_version_number(
    customer_id: int,
    doc_type: str,
    project_id: Optional[int] = None
) -> int:
    """
    Ermittelt die nächste Versionsnummer für einen Dokumenttyp.
    
    Args:
        customer_id: Kunden-ID
        doc_type: Dokumenttyp (z.B. 'offer_pdf')
        project_id: Optional - Projekt-ID für projektspezifische Versionierung
    
    Returns:
        Nächste Versionsnummer (1, 2, 3, ...)
    """
    try:
        from database import list_customer_documents
        
        # Alle Dokumente des Kunden abrufen
        docs = list_customer_documents(customer_id, project_id)
        
        # Dokumente des gleichen Typs filtern
        same_type_docs = [d for d in docs if d.get('doc_type') == doc_type]
        
        if not same_type_docs:
            return 1
        
        # Versionsnummern aus Dateinamen extrahieren
        max_version = 0
        for doc in same_type_docs:
            display_name = doc.get('display_name', '')
            # Suche nach Mustern wie "v1", "v2", "Version 1", etc.
            version_match = re.search(r'v(\d+)|version[_\s]?(\d+)', display_name, re.IGNORECASE)
            if version_match:
                version_num = int(version_match.group(1) or version_match.group(2))
                max_version = max(max_version, version_num)
        
        return max_version + 1
        
    except Exception as e:
        print(f"PDF Bridge: Fehler beim Ermitteln der Versionsnummer: {e}")
        return 1


def create_versioned_filename(
    original_filename: str,
    version: int,
    metadata: dict[str, Any]
) -> str:
    """
    Erstellt einen versionierten Dateinamen.
    
    Args:
        original_filename: Original-Dateiname
        version: Versionsnummer
        metadata: Metadaten für zusätzliche Informationen
    
    Returns:
        Versionierter Dateiname
    """
    # Dateiname und Erweiterung trennen
    name_parts = os.path.splitext(original_filename)
    base_name = name_parts[0]
    extension = name_parts[1] if len(name_parts) > 1 and name_parts[1] else '.pdf'
    
    # Datum formatieren
    date_str = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Versionierten Namen erstellen
    versioned_name = f"{base_name}_v{version}_{date_str}{extension}"
    
    return versioned_name


def auto_save_pdf_to_customer_documents(
    pdf_path: str,
    customer_id: int,
    project_id: Optional[int] = None,
    offer_data: Optional[dict[str, Any]] = None,
    display_name: Optional[str] = None
) -> Optional[int]:
    """
    Speichert ein PDF automatisch in der Kundenakte mit Metadaten und Versionierung.
    
    Args:
        pdf_path: Pfad zur PDF-Datei
        customer_id: Kunden-ID
        project_id: Optional - Projekt-ID
        offer_data: Optional - Angebotsdaten für Metadaten
        display_name: Optional - Anzeigename (wird automatisch generiert wenn nicht angegeben)
    
    Returns:
        Dokument-ID bei Erfolg, None bei Fehler
    """
    try:
        from database import add_customer_document, get_db_connection
        
        # Prüfen ob Datei existiert
        if not os.path.exists(pdf_path):
            print(f"PDF Bridge: Datei nicht gefunden: {pdf_path}")
            return None
        
        # Metadaten extrahieren
        metadata = extract_pdf_metadata(pdf_path, offer_data)
        
        # Versionsnummer ermitteln
        version = get_next_version_number(
            customer_id,
            metadata['doc_type'],
            project_id
        )
        metadata['version'] = version
        
        # PDF-Datei einlesen
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Display-Name erstellen wenn nicht angegeben
        if not display_name:
            original_filename = os.path.basename(pdf_path)
            display_name = create_versioned_filename(
                original_filename,
                version,
                metadata
            )
        else:
            # Versionsnummer zum Display-Name hinzufügen
            display_name = create_versioned_filename(
                display_name,
                version,
                metadata
            )
        
        # Suggested filename für Dateisystem
        suggested_filename = display_name
        
        # In Kundenakte speichern
        doc_id = add_customer_document(
            customer_id=customer_id,
            file_bytes=pdf_bytes,
            display_name=display_name,
            doc_type=metadata['doc_type'],
            project_id=project_id,
            suggested_filename=suggested_filename
        )
        
        if doc_id:
            print(f"PDF Bridge: PDF erfolgreich gespeichert - Dokument-ID: {doc_id}")
            print(f"  • Kunde: {customer_id}")
            print(f"  • Typ: {metadata['doc_type']}")
            print(f"  • Version: {version}")
            print(f"  • Größe: {metadata['file_size'] / 1024:.1f} KB")
            
            # Automatische Angebotsstatus-Aktualisierung bei Angebots-PDFs
            if metadata['doc_type'] == 'offer_pdf' and project_id:
                try:
                    from crm.features.offer_tracker import update_offer_status
                    
                    conn = get_db_connection()
                    if conn:
                        # Ermittle Angebotswert aus offer_data falls vorhanden
                        offer_value = None
                        if offer_data:
                            offer_value = offer_data.get('total_cost') or offer_data.get('offer_value')
                        
                        # Aktualisiere Status auf "sent" mit automatischem Follow-up
                        success = update_offer_status(
                            conn,
                            project_id,
                            'sent',
                            offer_value=offer_value,
                            offer_version=version
                        )
                        
                        if success:
                            print(f"PDF Bridge: Angebotsstatus automatisch auf 'sent' aktualisiert")
                            print(f"  • Follow-up-Erinnerung in 7 Tagen erstellt")
                        
                        conn.close()
                        
                except ImportError:
                    print("PDF Bridge: Offer Tracker nicht verfügbar, Status-Update übersprungen")
                except Exception as e:
                    print(f"PDF Bridge: Fehler bei automatischer Status-Aktualisierung: {e}")
        else:
            print(f"PDF Bridge: Fehler beim Speichern des PDFs")
        
        return doc_id
        
    except Exception as e:
        print(f"PDF Bridge: Fehler bei auto_save_pdf_to_customer_documents: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_customer_id_from_session() -> Optional[int]:
    """
    Versucht die Kunden-ID aus dem Streamlit Session State zu ermitteln.
    
    Returns:
        Kunden-ID oder None
    """
    try:
        import streamlit as st
        
        # Verschiedene mögliche Keys prüfen
        possible_keys = [
            'current_customer_id',
            'selected_customer_id',
            'customer_id',
            'crm_current_customer_id'
        ]
        
        for key in possible_keys:
            if key in st.session_state:
                customer_id = st.session_state[key]
                if customer_id and isinstance(customer_id, int):
                    return customer_id
        
        # Fallback: Aus current_customer Dictionary
        if 'current_customer' in st.session_state:
            current_customer = st.session_state['current_customer']
            if isinstance(current_customer, dict) and 'id' in current_customer:
                return current_customer['id']
        
        return None
        
    except Exception as e:
        print(f"PDF Bridge: Fehler beim Ermitteln der Kunden-ID: {e}")
        return None


def get_project_id_from_session() -> Optional[int]:
    """
    Versucht die Projekt-ID aus dem Streamlit Session State zu ermitteln.
    
    Returns:
        Projekt-ID oder None
    """
    try:
        import streamlit as st
        
        # Verschiedene mögliche Keys prüfen
        possible_keys = [
            'current_project_id',
            'selected_project_id',
            'project_id',
            'crm_current_project_id'
        ]
        
        for key in possible_keys:
            if key in st.session_state:
                project_id = st.session_state[key]
                if project_id and isinstance(project_id, int):
                    return project_id
        
        return None
        
    except Exception as e:
        print(f"PDF Bridge: Fehler beim Ermitteln der Projekt-ID: {e}")
        return None


def get_pdf_type_badge_color(doc_type: str) -> str:
    """
    Gibt die Badge-Farbe für einen PDF-Typ zurück.
    
    Args:
        doc_type: Dokumenttyp
    
    Returns:
        Farbe als Hex-Code
    """
    color_map = {
        'offer_pdf': '#2563EB',      # Blau
        'invoice_pdf': '#22C55E',    # Grün
        'contract_pdf': '#F59E0B',   # Orange
        'report_pdf': '#8B5CF6',     # Violett
        'other_pdf': '#64748B'       # Grau
    }
    
    return color_map.get(doc_type, '#64748B')


def get_pdf_type_label(doc_type: str) -> str:
    """
    Gibt das deutsche Label für einen PDF-Typ zurück.
    
    Args:
        doc_type: Dokumenttyp
    
    Returns:
        Deutsches Label
    """
    label_map = {
        'offer_pdf': 'Angebot',
        'invoice_pdf': 'Rechnung',
        'contract_pdf': 'Vertrag',
        'report_pdf': 'Bericht',
        'other_pdf': 'Sonstiges'
    }
    
    return label_map.get(doc_type, 'Dokument')



def show_customer_assignment_dialog() -> Optional[int]:
    """
    Zeigt einen Dialog zur Kundenzuordnung an (Streamlit UI).
    
    Returns:
        Ausgewählte Kunden-ID oder None
    """
    try:
        import streamlit as st
        from database import get_db_connection
        
        st.warning("Kein Kunde zugeordnet - PDF wird nicht automatisch archiviert")
        
        with st.expander("📋 Kunde für PDF-Archivierung auswählen", expanded=False):
            st.info("Wählen Sie einen Kunden aus, um das PDF automatisch in der Kundenakte zu speichern.")
            
            # Kundenliste abrufen
            conn = get_db_connection()
            if not conn:
                st.error("Datenbankverbindung fehlgeschlagen")
                return None
            
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, email, company 
                    FROM customers 
                    ORDER BY name
                """)
                customers = cursor.fetchall()
                
                if not customers:
                    st.warning("Keine Kunden in der Datenbank gefunden")
                    return None
                
                # Dropdown mit Kunden
                customer_options = {
                    f"{row['name']} ({row['email'] or row['company'] or 'Keine E-Mail'})": row['id']
                    for row in customers
                }
                
                selected_customer = st.selectbox(
                    "Kunde auswählen:",
                    options=list(customer_options.keys()),
                    key="pdf_customer_assignment"
                )
                
                if st.button("Kunde zuordnen und PDF archivieren", key="assign_customer_pdf"):
                    customer_id = customer_options[selected_customer]
                    st.success(f"Kunde zugeordnet: {selected_customer}")
                    return customer_id
                
            finally:
                conn.close()
        
        return None
        
    except Exception as e:
        print(f"PDF Bridge: Fehler bei show_customer_assignment_dialog: {e}")
        return None


def format_document_list_for_display(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Formatiert eine Dokumentenliste für die Anzeige mit zusätzlichen Informationen.
    
    Args:
        docs: Liste von Dokumenten aus der Datenbank
    
    Returns:
        Formatierte Dokumentenliste mit zusätzlichen Display-Feldern
    """
    formatted_docs = []
    
    for doc in docs:
        formatted_doc = doc.copy()
        
        # Typ-Label hinzufügen
        formatted_doc['type_label'] = get_pdf_type_label(doc.get('doc_type', ''))
        
        # Badge-Farbe hinzufügen
        formatted_doc['badge_color'] = get_pdf_type_badge_color(doc.get('doc_type', ''))
        
        # Versionsnummer extrahieren
        display_name = doc.get('display_name', '')
        version_match = re.search(r'v(\d+)', display_name, re.IGNORECASE)
        formatted_doc['version'] = int(version_match.group(1)) if version_match else None
        
        # Datum formatieren
        uploaded_at = doc.get('uploaded_at', '')
        if uploaded_at:
            try:
                from datetime import datetime
                if 'T' in uploaded_at:
                    dt = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(uploaded_at, '%Y-%m-%d %H:%M:%S')
                formatted_doc['formatted_date'] = dt.strftime('%d.%m.%Y %H:%M')
            except Exception:
                formatted_doc['formatted_date'] = uploaded_at
        else:
            formatted_doc['formatted_date'] = '-'
        
        formatted_docs.append(formatted_doc)
    
    return formatted_docs
