"""
Drawer Quick Actions Handler
============================

Funktionsmodul für die 5 erweiterten Drawer-Buttons.
Unterstützt:
- Button 1: Sprachbefehl (Speech-to-Text Agent-Steuerung)
- Button 2: 3D Visualisierung (Shortcut mit PV-Warnung)
- Button 3: Kunde ins CRM speichern
- Button 4: Blitz-Angebot (Schnell-PDF ohne UI)
- Button 5: Hilfe-Menü (FAQ/Help aus allen MD-Dateien)
"""

import streamlit as st
import sqlite3
import os
import glob
from pathlib import Path
from typing import Optional
import base64


def handle_drawer_action_voice_command():
    """
    Button 1: Sprachbefehl
    Aktiviert Speech-to-Text für Agent-Steuerung
    """
    st.session_state['drawer_voice_active'] = True
    st.session_state['active_page'] = 'agent_ui'
    st.session_state['selected_page_key_sui'] = 'agent_ui'
    st.session_state['voice_mode'] = True
    

def handle_drawer_action_3d_visualization():
    """
    Button 2: 3D Visualisierung
    Shortcut zu 3D PV-Menü mit Wärmepumpen-Warnung
    """
    # Check if heat pump calculation is active
    is_heatpump_mode = st.session_state.get('active_page') == 'heatpump'
    
    if is_heatpump_mode:
        st.session_state['drawer_3d_warning'] = True
        return False
    
    # Switch to 3D view
    st.session_state['active_page'] = '3d_view'
    st.session_state['selected_page_key_sui'] = '3d_view'
    return True


def handle_drawer_action_save_customer():
    """
    Button 3: Kunde ins CRM speichern
    Speichert aktuellen Kunden mit allen Daten ins CRM
    """
    try:
        from crm import save_customer
        from database import get_connection
        
        # Sammle Kundendaten aus Session
        customer_data = {
            'first_name': st.session_state.get('customer_first_name', ''),
            'last_name': st.session_state.get('customer_last_name', ''),
            'email': st.session_state.get('customer_email', ''),
            'phone': st.session_state.get('customer_phone', ''),
            'street': st.session_state.get('customer_street', ''),
            'city': st.session_state.get('customer_city', ''),
            'zip': st.session_state.get('customer_zip', ''),
            'company': st.session_state.get('customer_company', ''),
            'notes': st.session_state.get('customer_notes', ''),
        }
        
        # Check if minimal data available
        if not customer_data['first_name'] and not customer_data['last_name'] and not customer_data['email']:
            st.session_state['drawer_customer_error'] = "Bitte geben Sie mindestens Name oder E-Mail ein."
            return False
        
        # Save to CRM
        conn = get_connection()
        customer_id = save_customer(conn, customer_data)
        conn.close()
        
        st.session_state['drawer_customer_success'] = f"Kunde erfolgreich gespeichert! (ID: {customer_id})"
        return True
        
    except Exception as e:
        st.session_state['drawer_customer_error'] = f"Fehler beim Speichern: {str(e)}"
        return False


def handle_drawer_action_quick_pdf():
    """
    Button 4: Blitz-Angebot
    Erstellt Standard-PDF direkt ohne UI
    """
    try:
        from pdf_generator import generate_offer_pdf
        from database import get_connection
        
        # Hole aktuelle Session-Daten
        conn = get_connection()
        
        # Erstelle PDF mit aktuellen Daten
        pdf_bytes = generate_offer_pdf(
            conn=conn,
            texts=st.session_state.get('texts', {}),
            customer_data=st.session_state.get('customer_data', {}),
            system_data=st.session_state.get('system_data', {}),
            prices=st.session_state.get('prices', {}),
            economic_data=st.session_state.get('economic_data', {}),
            calculation_results=st.session_state.get('calculation_results', {}),
            heatpump_results=st.session_state.get('heatpump_results', None),
            admin_settings=st.session_state.get('admin_settings', {})
        )
        
        conn.close()
        
        if pdf_bytes:
            # Speichere PDF
            output_dir = Path('data/pdf_output')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            pdf_path = output_dir / 'blitz_angebot.pdf'
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            st.session_state['drawer_pdf_success'] = str(pdf_path)
            st.session_state['drawer_pdf_bytes'] = pdf_bytes
            return True
        else:
            st.session_state['drawer_pdf_error'] = "PDF-Generierung fehlgeschlagen (keine Daten)"
            return False
            
    except Exception as e:
        st.session_state['drawer_pdf_error'] = f"Fehler bei PDF-Erstellung: {str(e)}"
        return False


def render_help_menu():
    """
    Button 5: Hilfe-Menü
    Zeigt FAQ/Help-Seite (ohne Dokumentation - die ist jetzt im Admin-Bereich)
    """
    st.markdown("# 📚 Hilfe & Support")
    st.markdown("---")
    
    st.markdown("""
    ## Willkommen im Hilfe-Menü
    
    Hier finden Sie schnelle Antworten auf häufige Fragen zur Nutzung der Anwendung.
    
    ### Quick Links:
    - **Agent**: KI-Assistent für Berechnungen und Analysen
    - **Solar Calculator**: PV-Anlagen berechnen
    - **3D Visualisierung**: Interaktive 3D-Darstellung
    - **Wärmepumpe**: Wärmepumpen-Berechnungen
    - **CRM**: Kundenverwaltung
    - **Admin**: Systemeinstellungen
    
    ---
    
    ### [TARGET] Häufige Fragen (FAQ):
    
    #### **Q: Wie erstelle ich ein Angebot?**
    A: Gehen Sie zu "Dateneingabe", füllen Sie die Kundendaten aus, und klicken Sie auf "PDF erstellen".
    
    #### **Q: Wie speichere ich einen Kunden?**
    A: Nutzen Sie den Quick Action Button "💾 Kunde ins CRM" im Drawer (unten rechts) oder gehen Sie ins CRM-Modul.
    
    #### **Q: Wie funktioniert der Blitz-Angebot Button?**
    A: Der Button "[POWER] Blitz-Angebot" erstellt sofort ein Standard-PDF mit den aktuellen Daten, ohne zusätzliche UI-Schritte.
    
    #### **Q: Was macht der Sprachbefehl-Button?**
    A: Der Button "🎤 Sprachbefehl" aktiviert die Sprachsteuerung für den KI-Agent.
    
    #### **Q: Wo finde ich die vollständige Dokumentation?**
    A: Die vollständige Dokumentation (Hauptdokumentation + Detaillierte Docs) befindet sich im **Admin-Bereich** unter dem Tab **"Build Infos"** (passwortgeschützt).
    
    #### **Q: Wie funktioniert die 3D-Visualisierung?**
    A: Klicken Sie auf "🏠 3D Visualisierung" im Drawer. Die Funktion zeigt interaktive 3D-Modelle von Wärmepumpen-Systemen.
    
    #### **Q: Was passiert bei Logout?**
    A: Alle Session-Daten werden gelöscht, und Sie werden zur Login-Seite weitergeleitet.
    
    ---
    
    ### [IDEA] Tipps & Tricks:
    
    - **Drawer**: Nutzen Sie das ☰ Symbol unten rechts für schnelle Aktionen
    - **Agent**: Der KI-Agent kann komplexe Berechnungen durchführen und Fragen beantworten
    - **Hotkeys**: Verwenden Sie Tastenkombinationen für schnelleres Arbeiten
    - **Admin-Panel**: Umfangreiche Einstellungen und Dokumentation im Admin-Bereich
    
    ---
    
    ### 📞 Support:
    
    Bei weiteren Fragen wenden Sie sich bitte an:
    - **E-Mail**: support@example.com
    - **Telefon**: +49 123 456789
    - **Admin**: Technische Dokumentation im Admin-Bereich (Build Infos Tab)
    """)
    
    st.markdown("---")
    st.info("[IDEA] **Hinweis**: Die vollständige Build-Dokumentation finden Sie im Admin-Bereich unter 'Build Infos' (passwortgeschützt).")


def show_drawer_notifications():
    """
    Zeigt Feedback-Meldungen für Drawer-Aktionen
    """
    # 3D Warnung
    if st.session_state.get('drawer_3d_warning'):
        st.warning("[WARNING] 3D-Visualisierung ist nur für PV-Berechnungen verfügbar, nicht für Wärmepumpen.")
        st.session_state['drawer_3d_warning'] = False
    
    # Kunden-Speicherung
    if st.session_state.get('drawer_customer_success'):
        st.success(st.session_state['drawer_customer_success'])
        st.session_state['drawer_customer_success'] = None
    
    if st.session_state.get('drawer_customer_error'):
        st.error(st.session_state['drawer_customer_error'])
        st.session_state['drawer_customer_error'] = None
    
    # PDF-Erstellung
    if st.session_state.get('drawer_pdf_success'):
        st.success(f"[OK] Blitz-Angebot erstellt: {st.session_state['drawer_pdf_success']}")
        
        # Download-Button
        if st.session_state.get('drawer_pdf_bytes'):
            st.download_button(
                label="📥 PDF herunterladen",
                data=st.session_state['drawer_pdf_bytes'],
                file_name="blitz_angebot.pdf",
                mime="application/pdf"
            )
            st.session_state['drawer_pdf_bytes'] = None
        
        st.session_state['drawer_pdf_success'] = None
    
    if st.session_state.get('drawer_pdf_error'):
        st.error(st.session_state['drawer_pdf_error'])
        st.session_state['drawer_pdf_error'] = None
