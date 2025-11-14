# crm/features/contract_integration_example.py
"""
Beispiele für die Integration der Vertrags- und Garantieverwaltung

Author: Kiro AI Assistant
Version: 1.0
Date: 2025-01-14
"""

from database import get_db_connection
from crm.features import contract_manager
from datetime import datetime, timedelta


def example_1_create_contract_with_warranty():
    """Beispiel 1: Vertrag und Garantie für neues Projekt erstellen"""
    print("\n=== Beispiel 1: Vertrag und Garantie erstellen ===")
    
    conn = get_db_connection()
    if not conn:
        print("Fehler: Keine Datenbankverbindung")
        return
    
    try:
        # 1. Kaufvertrag erstellen
        contract_id = contract_manager.create_contract(
            conn,
            customer_id=1,
            project_id=1,
            contract_type="Kaufvertrag",
            title="PV-Anlage Kaufvertrag",
            start_date=datetime.now().strftime('%Y-%m-%d'),
            value=25000.0,
            description="Kauf und Installation einer 10 kWp PV-Anlage",
            created_by="System"
        )
        print(f"[OK] Kaufvertrag erstellt (ID: {contract_id})")
        
        # 2. Produktgarantie hinzufügen (25 Jahre)
        warranty_id = contract_manager.create_warranty(
            conn,
            project_id=1,
            customer_id=1,
            warranty_type="Produktgarantie",
            title="PV-Module Produktgarantie",
            start_date=datetime.now().strftime('%Y-%m-%d'),
            duration_months=300,  # 25 Jahre
            provider="Trina Solar",
            terms="Garantie auf Materialfehler und Verarbeitung",
            created_by="System"
        )
        print(f"[OK] Produktgarantie erstellt (ID: {warranty_id})")
        
        # 3. Leistungsgarantie hinzufügen (25 Jahre)
        warranty_id2 = contract_manager.create_warranty(
            conn,
            project_id=1,
            customer_id=1,
            warranty_type="Leistungsgarantie",
            title="PV-Module Leistungsgarantie",
            start_date=datetime.now().strftime('%Y-%m-%d'),
            duration_months=300,
            provider="Trina Solar",
            terms="Mindestens 80% Leistung nach 25 Jahren",
            coverage_details="Jahr 1-10: 90%, Jahr 11-25: 80%",
            created_by="System"
        )
        print(f"[OK] Leistungsgarantie erstellt (ID: {warranty_id2})")
        
    finally:
        conn.close()


def example_2_create_maintenance_contract():
    """Beispiel 2: Wartungsvertrag mit automatischer Verlängerung"""
    print("\n=== Beispiel 2: Wartungsvertrag erstellen ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Wartungsvertrag für 1 Jahr
        start_date = datetime.now()
        end_date = start_date + timedelta(days=365)
        
        contract_id = contract_manager.create_contract(
            conn,
            customer_id=1,
            project_id=1,
            contract_type="Wartungsvertrag",
            title="Jährliche PV-Wartung",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            value=500.0,
            renewal_type="Automatisch",
            notice_period_days=30,
            description="Jährliche Inspektion und Wartung der PV-Anlage",
            created_by="System"
        )
        print(f"[OK] Wartungsvertrag erstellt (ID: {contract_id})")
        print(f"   Läuft ab am: {end_date.strftime('%Y-%m-%d')}")
        print(f"   Erinnerung wird erstellt für: {(end_date - timedelta(days=30)).strftime('%Y-%m-%d')}")
        
    finally:
        conn.close()


def example_3_check_expiring_contracts():
    """Beispiel 3: Ablaufende Verträge und Garantien prüfen"""
    print("\n=== Beispiel 3: Ablaufende Verträge prüfen ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Verträge die in 30 Tagen ablaufen
        expiring_contracts = contract_manager.get_expiring_contracts(conn, days_ahead=30)
        print(f"\n[FILE] Ablaufende Verträge (30 Tage): {len(expiring_contracts)}")
        for contract in expiring_contracts:
            days_left = (datetime.strptime(contract['end_date'], '%Y-%m-%d') - datetime.now()).days
            print(f"   - {contract['title']}: {days_left} Tage")
        
        # Garantien die in 30 Tagen ablaufen
        expiring_warranties = contract_manager.get_expiring_warranties(conn, days_ahead=30)
        print(f"\n🛡️ Ablaufende Garantien (30 Tage): {len(expiring_warranties)}")
        for warranty in expiring_warranties:
            days_left = (datetime.strptime(warranty['end_date'], '%Y-%m-%d') - datetime.now()).days
            print(f"   - {warranty['title']}: {days_left} Tage")
        
        # Fällige Erinnerungen
        reminders = contract_manager.get_pending_reminders(conn, days_ahead=7)
        print(f"\n⏰ Fällige Erinnerungen (7 Tage): {len(reminders)}")
        for reminder in reminders:
            print(f"   - {reminder['message']} am {reminder['reminder_date']}")
        
    finally:
        conn.close()


def example_4_customer_contracts_overview():
    """Beispiel 4: Alle Verträge und Garantien eines Kunden anzeigen"""
    print("\n=== Beispiel 4: Kunden-Übersicht ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        customer_id = 1
        
        # Alle Verträge des Kunden
        contracts = contract_manager.get_contracts_by_customer(conn, customer_id)
        print(f"\n[FILE] Verträge von Kunde {customer_id}: {len(contracts)}")
        for contract in contracts:
            status_icon = "[OK]" if contract['status'] == 'active' else "[ERROR]"
            print(f"   {status_icon} {contract['title']} ({contract['contract_type']})")
            if contract.get('value'):
                print(f"      Wert: {contract['value']:.2f} EUR")
        
        # Alle Garantien des Kunden
        warranties = contract_manager.get_warranties_by_customer(conn, customer_id)
        print(f"\n🛡️ Garantien von Kunde {customer_id}: {len(warranties)}")
        for warranty in warranties:
            status_icon = "[OK]" if warranty['status'] == 'active' else "[ERROR]"
            print(f"   {status_icon} {warranty['title']} ({warranty['warranty_type']})")
            print(f"      Läuft bis: {warranty['end_date']}")
        
    finally:
        conn.close()


def example_5_statistics_dashboard():
    """Beispiel 5: Statistiken für Dashboard"""
    print("\n=== Beispiel 5: Statistiken ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Vertrags-Statistiken
        contract_stats = contract_manager.get_contract_statistics(conn)
        print("\n[CHART] Vertrags-Statistiken:")
        print(f"   Gesamt: {contract_stats['total']}")
        print(f"   Aktiv: {contract_stats['by_status'].get('active', 0)}")
        print(f"   Abgelaufen: {contract_stats['expired']}")
        print(f"   Ablaufend (30 Tage): {contract_stats['expiring_30_days']}")
        print(f"   Gesamtwert: {contract_stats['total_value']:,.2f} EUR")
        
        if contract_stats['by_type']:
            print("\n   Nach Typ:")
            for contract_type, count in contract_stats['by_type'].items():
                print(f"      - {contract_type}: {count}")
        
        # Garantie-Statistiken
        warranty_stats = contract_manager.get_warranty_statistics(conn)
        print("\n🛡️ Garantie-Statistiken:")
        print(f"   Gesamt: {warranty_stats['total']}")
        print(f"   Aktiv: {warranty_stats['by_status'].get('active', 0)}")
        print(f"   Abgelaufen: {warranty_stats['expired']}")
        print(f"   Ablaufend (30 Tage): {warranty_stats['expiring_30_days']}")
        
        if warranty_stats['by_type']:
            print("\n   Nach Typ:")
            for warranty_type, count in warranty_stats['by_type'].items():
                print(f"      - {warranty_type}: {count}")
        
    finally:
        conn.close()


def example_6_extend_contract():
    """Beispiel 6: Vertrag verlängern"""
    print("\n=== Beispiel 6: Vertrag verlängern ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Angenommen wir haben einen Vertrag mit ID 1
        contract_id = 1
        
        # Lade aktuellen Vertrag
        contract = contract_manager.get_contract_by_id(conn, contract_id)
        if not contract:
            print("Vertrag nicht gefunden")
            return
        
        print(f"Aktueller Vertrag: {contract['title']}")
        print(f"Aktuelles Enddatum: {contract.get('end_date', 'Unbefristet')}")
        
        # Verlängere um 1 Jahr
        if contract.get('end_date'):
            current_end = datetime.strptime(contract['end_date'], '%Y-%m-%d')
            new_end = current_end + timedelta(days=365)
            
            success = contract_manager.update_contract(
                conn,
                contract_id,
                end_date=new_end.strftime('%Y-%m-%d'),
                updated_by="System"
            )
            
            if success:
                print(f"[OK] Vertrag verlängert bis: {new_end.strftime('%Y-%m-%d')}")
                print(f"   Neue Erinnerung wird erstellt für: {(new_end - timedelta(days=30)).strftime('%Y-%m-%d')}")
            else:
                print("[ERROR] Fehler beim Verlängern")
        
    finally:
        conn.close()


def example_7_archive_expired_contracts():
    """Beispiel 7: Abgelaufene Verträge archivieren"""
    print("\n=== Beispiel 7: Abgelaufene Verträge archivieren ===")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Finde alle abgelaufenen Verträge die noch als 'active' markiert sind
        expired = contract_manager.get_expired_contracts(conn)
        
        archived_count = 0
        for contract in expired:
            if contract['status'] == 'active':
                success = contract_manager.update_contract(
                    conn,
                    contract['id'],
                    status='expired',
                    updated_by="System"
                )
                if success:
                    archived_count += 1
                    print(f"[OK] Archiviert: {contract['title']}")
        
        print(f"\n[PACKAGE] {archived_count} Verträge archiviert")
        
    finally:
        conn.close()


def example_8_streamlit_integration():
    """Beispiel 8: Integration in Streamlit App"""
    print("\n=== Beispiel 8: Streamlit Integration ===")
    print("""
# In gui.py oder crm.py:

import streamlit as st
from crm.features.contract_ui import render_contract_management_ui
from crm.features.contract_ui import show_customer_contracts_warranties

# Option 1: Als eigener Menüpunkt
if selected_menu == "Verträge & Garantien":
    render_contract_management_ui()

# Option 2: In Kundendetailansicht
if customer_id:
    st.markdown("---")
    show_customer_contracts_warranties(customer_id)

# Option 3: Dashboard-Widget für Erinnerungen
from crm.features import contract_manager
conn = get_db_connection()
reminders = contract_manager.get_pending_reminders(conn, days_ahead=7)
if reminders:
    st.warning(f"[WARNING] {len(reminders)} Erinnerungen fällig!")
    for reminder in reminders:
        st.write(f"- {reminder['message']}")
conn.close()
    """)


def run_all_examples():
    """Führt alle Beispiele aus"""
    print("=" * 60)
    print("VERTRAGS- UND GARANTIEVERWALTUNG - BEISPIELE")
    print("=" * 60)
    
    try:
        example_1_create_contract_with_warranty()
        example_2_create_maintenance_contract()
        example_3_check_expiring_contracts()
        example_4_customer_contracts_overview()
        example_5_statistics_dashboard()
        example_6_extend_contract()
        example_7_archive_expired_contracts()
        example_8_streamlit_integration()
    except Exception as e:
        print(f"\n[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("BEISPIELE ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
