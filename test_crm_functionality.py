"""
Test CRM Kundenverwaltung

Testet alle wichtigen CRM-Funktionen.
"""

import sys
sys.path.insert(0, '.')

def test_crm_customer_management():
    """Testet die CRM Kundenverwaltung."""
    print("="*80)
    print("CRM KUNDENVERWALTUNG TEST")
    print("="*80)
    
    # Import CRM functions
    print("\nImportiere CRM-Funktionen...")
    try:
        import crm
        from database import get_db_connection
        print("Import erfolgreich")
    except Exception as e:
        print(f"Import fehlgeschlagen: {e}")
        return False
    
    # Test database connection
    print("\n  Teste Datenbankverbindung...")
    try:
        conn = get_db_connection()
        if not conn:
            print("Keine Datenbankverbindung")
            return False
        print("Datenbankverbindung hergestellt")
    except Exception as e:
        print(f"Fehler: {e}")
        return False
    
    # Test: Load all customers
    print("\n Teste: Alle Kunden laden...")
    try:
        customers = crm.load_all_customers(conn)
        print(f"{len(customers)} Kunden gefunden")
        if customers:
            print(f"   Beispiel: {customers[0].get('name', 'N/A')}")
    except Exception as e:
        print(f"Fehler beim Laden: {e}")
        return False
    
    # Test: Create test customer
    print("\n Teste: Neuen Test-Kunden erstellen...")
    try:
        test_customer = {
            'name': 'Test Kunde',
            'email': 'test@example.com',
            'phone': '0123456789',
            'address': 'Teststraße 123',
            'city': 'Teststadt',
            'zip': '12345'
        }
        customer_id = crm.save_customer(conn, test_customer)
        if customer_id:
            print(f"Kunde erstellt mit ID: {customer_id}")
        else:
            print("Kunde konnte nicht erstellt werden")
    except Exception as e:
        print(f"Fehler beim Erstellen: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test: Load customer
    if customer_id:
        print(f"\nTeste: Kunde {customer_id} laden...")
        try:
            loaded = crm.load_customer(conn, customer_id)
            if loaded:
                print(f"Kunde geladen: {loaded.get('name')}")
                print(f"   Email: {loaded.get('email')}")
                print(f"   Stadt: {loaded.get('city')}")
            else:
                print("Kunde nicht gefunden")
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
    
    # Test: Delete test customer
    if customer_id:
        print(f"\nTeste: Test-Kunde {customer_id} löschen...")
        try:
            success = crm.delete_customer(conn, customer_id)
            if success:
                print("Kunde gelöscht")
            else:
                print("Kunde konnte nicht gelöscht werden")
        except Exception as e:
            print(f"Fehler beim Löschen: {e}")
    
    # Clean up
    conn.close()
    
    print("\n" + "="*80)
    print("CRM KUNDENVERWALTUNG TEST ABGESCHLOSSEN")
    print("="*80)
    return True


if __name__ == "__main__":
    success = test_crm_customer_management()
    sys.exit(0 if success else 1)
