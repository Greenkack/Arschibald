"""
Demo-Script: Agentname-Integration Controlling System

Zeigt die Verwendung der Agentname-Funktionalität.
"""

from datetime import date
from controlling.managers import EmployeeManager, PositionManager
from controlling.utils import (
    get_agent_name_by_employee_id,
    enrich_customer_data_with_agent_name,
    get_all_active_employees
)
from backend.core.database import SessionLocal


def demo_create_employee_with_agent_name():
    """Demo: Mitarbeiter mit Agentname erstellen"""
    print("\n" + "="*60)
    print("DEMO 1: Mitarbeiter mit Agentname erstellen")
    print("="*60)
    
    db = SessionLocal()
    emp_manager = EmployeeManager(db)
    pos_manager = PositionManager(db)
    
    try:
        # Erstelle Position falls nicht vorhanden
        positions = pos_manager.list_positions()
        if not positions:
            print("Erstelle Demo-Position...")
            position = pos_manager.create_position(
                name="Vertriebsmitarbeiter",
                description="Außendienst Photovoltaik"
            )
            position_id = position.id
        else:
            position_id = positions[0].id
            print(f"Verwende existierende Position: {positions[0].name}")
        
        # Erstelle Mitarbeiter mit Agentname
        print("\nErstelle Mitarbeiter mit Agentname...")
        employee = emp_manager.create_employee(
            first_name="Hans",
            last_name="Schmidt",
            agent_name="Vertriebsberater Nord",  # NEU: Agentname
            city="Hamburg",
            birth_date=date(1985, 3, 15),
            position_id=position_id,
            start_date=date(2023, 1, 1)
        )
        
        print(f"\nMitarbeiter erstellt:")
        print(f"  ID: {employee.id}")
        print(f"  Name: {employee.full_name}")
        print(f"  Agentname: {employee.agent_name}")
        print(f"  Position: {employee.position.name}")
        
        return employee.id
        
    except Exception as e:
        print(f"Fehler: {e}")
        return None
    finally:
        db.close()


def demo_get_agent_name(employee_id):
    """Demo: Agentname abrufen"""
    print("\n" + "="*60)
    print("DEMO 2: Agentname aus Datenbank abrufen")
    print("="*60)
    
    agent_name = get_agent_name_by_employee_id(employee_id)
    
    if agent_name:
        print(f"\nAgent-Name für Employee ID {employee_id}: '{agent_name}'")
    else:
        print(f"\nKein Agent-Name gefunden für Employee ID {employee_id}")
    
    return agent_name


def demo_enrich_customer_data(employee_id):
    """Demo: Customer-Data mit Agentname anreichern"""
    print("\n" + "="*60)
    print("DEMO 3: Customer-Data für PDF anreichern")
    print("="*60)
    
    # Beispiel Customer-Data (wie aus CRM/Formular)
    customer_data = {
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com',
        'city': 'Berlin',
        'zip_code': '10115'
    }
    
    print("\nVorher (ohne Agentname):")
    print(f"  {customer_data}")
    
    # Anreichern mit Agentname
    enriched_data = enrich_customer_data_with_agent_name(
        customer_data,
        employee_id=employee_id
    )
    
    print("\nNachher (mit Agentname):")
    print(f"  {enriched_data}")
    print(f"\n  → Agent-Name: '{enriched_data.get('agent_name', 'Nicht gesetzt')}'")
    
    return enriched_data


def demo_list_all_employees():
    """Demo: Alle Mitarbeiter auflisten"""
    print("\n" + "="*60)
    print("DEMO 4: Alle aktiven Mitarbeiter mit Agentname")
    print("="*60)
    
    employees = get_all_active_employees()
    
    if not employees:
        print("\nKeine aktiven Mitarbeiter gefunden.")
        return
    
    print(f"\nGefundene Mitarbeiter: {len(employees)}")
    print("\n{:<5} {:<25} {:<30} {:<20}".format(
        "ID", "Name", "Agentname", "Position"
    ))
    print("-" * 80)
    
    for emp in employees:
        print("{:<5} {:<25} {:<30} {:<20}".format(
            emp.id,
            emp.full_name,
            emp.agent_name or "(nicht angegeben)",
            emp.position.name if emp.position else "N/A"
        ))


def demo_pdf_placeholder_usage():
    """Demo: PDF-Platzhalter Verwendung"""
    print("\n" + "="*60)
    print("DEMO 5: PDF-Platzhalter für Agentname")
    print("="*60)
    
    print("\nIn PDF-Textvorlagen (Anschreiben, etc.) verwenden:")
    print("-" * 60)
    
    template_example = """
Sehr geehrte/r [VollständigeAnrede],

vielen Dank für Ihr Interesse an einer Photovoltaik-Anlage.

Ihr persönlicher Ansprechpartner:
[Agentname]

Angebotsnummer: [Angebotsnummer]
Datum: [Datum]

Mit freundlichen Grüßen,
[Ihr Name/Firmenname]
    """
    
    print(template_example)
    print("-" * 60)
    print("\nDer Platzhalter [Agentname] wird automatisch ersetzt durch")
    print("den Wert aus customer_data['agent_name']")
    
    print("\n\nBeispiel-Code für PDF-Generierung:")
    print("-" * 60)
    code_example = """
from controlling.utils import enrich_customer_data_with_agent_name

# 1. Customer-Data vorbereiten
customer_data = {
    'first_name': 'Max',
    'last_name': 'Mustermann',
    # ... weitere Felder ...
}

# 2. Mit Agentname anreichern
customer_data = enrich_customer_data_with_agent_name(
    customer_data,
    employee_id=selected_employee_id  # z.B. aus Session State
)

# 3. PDF generieren (Platzhalter wird automatisch ersetzt)
pdf_bytes = generate_offer_pdf(
    customer_data=customer_data,
    # ... weitere Parameter ...
)
    """
    print(code_example)


def run_all_demos():
    """Führe alle Demos aus"""
    print("\n" + "="*60)
    print("AGENTNAME-INTEGRATION DEMO")
    print("="*60)
    print("\nDieses Script demonstriert die Verwendung der Agentname-")
    print("Funktionalität im Controlling-System.")
    
    # Demo 1: Mitarbeiter erstellen
    employee_id = demo_create_employee_with_agent_name()
    
    if employee_id:
        # Demo 2: Agentname abrufen
        demo_get_agent_name(employee_id)
        
        # Demo 3: Customer-Data anreichern
        demo_enrich_customer_data(employee_id)
    
    # Demo 4: Alle Mitarbeiter listen
    demo_list_all_employees()
    
    # Demo 5: PDF-Platzhalter
    demo_pdf_placeholder_usage()
    
    print("\n" + "="*60)
    print("DEMO ABGESCHLOSSEN")
    print("="*60)
    print("\nWeitere Informationen:")
    print("  - AGENTNAME_INTEGRATION.md")
    print("  - controlling/utils.py")
    print("  - admin_controlling_settings_ui.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_demos()
