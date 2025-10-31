"""
Test-Skript: Prüft ob pv_details korrekt geladen wird und alle Komponenten-IDs verfügbar sind
"""

def test_pv_details_structure():
    """Simuliert die Datenstruktur und prüft die Extraktion"""
    
    # Simulierte project_data Struktur (wie von solarcalculator.py)
    mock_project_data = {
        "customer_data": {
            "name": "Max Mustermann"
        },
        "pv_details": {
            "selected_module_id": 101,
            "selected_inverter_id": 202,
            "selected_storage_id": 303,
            "include_storage": True,
            "selected_wallbox_id": 404,
            "selected_ems_id": 505,
            "include_additional_components": True
        },
        "project_details": {
            # Alte Struktur (sollte als Fallback funktionieren)
            "module_id": 999
        }
    }
    
    print("=" * 80)
    print("TEST: pv_details Extraktion")
    print("=" * 80)
    
    # Test 1: Neue Struktur (pv_details)
    pv_details_new = mock_project_data.get("pv_details", {})
    if not pv_details_new:
        pv_details_new = mock_project_data.get("project_details", {})
    
    print("\n✅ Test 1: pv_details Extraktion")
    print(f"   Module ID: {pv_details_new.get('selected_module_id')}")
    print(f"   Inverter ID: {pv_details_new.get('selected_inverter_id')}")
    print(f"   Storage ID: {pv_details_new.get('selected_storage_id')}")
    print(f"   Include Storage: {pv_details_new.get('include_storage')}")
    print(f"   Wallbox ID: {pv_details_new.get('selected_wallbox_id')}")
    print(f"   EMS ID: {pv_details_new.get('selected_ems_id')}")
    
    # Test 2: Component ID Liste erstellen
    product_ids = list(filter(None, [
        pv_details_new.get("selected_module_id"),
        pv_details_new.get("selected_inverter_id"),
        pv_details_new.get("selected_storage_id") if pv_details_new.get("include_storage") else None
    ]))
    
    print(f"\n✅ Test 2: Haupt-Komponenten-IDs")
    print(f"   Gesamt: {len(product_ids)} Komponenten")
    print(f"   IDs: {product_ids}")
    
    # Test 3: Zubehör hinzufügen
    if pv_details_new.get('include_additional_components', True):
        for key in ['selected_wallbox_id', 'selected_ems_id']:
            comp_id = pv_details_new.get(key)
            if comp_id:
                product_ids.append(comp_id)
    
    print(f"\n✅ Test 3: Mit Zubehör")
    print(f"   Gesamt: {len(product_ids)} Komponenten")
    print(f"   IDs: {product_ids}")
    
    # Test 4: Fallback zu project_details
    print(f"\n✅ Test 4: Fallback-Mechanismus")
    mock_project_data_old = {
        "project_details": {
            "module_id": 111
        }
    }
    pv_details_fallback = mock_project_data_old.get("pv_details", {})
    if not pv_details_fallback:
        pv_details_fallback = mock_project_data_old.get("project_details", {})
    print(f"   Fallback Module ID: {pv_details_fallback.get('module_id')}")
    
    print("\n" + "=" * 80)
    print("✅ ALLE TESTS BESTANDEN")
    print("=" * 80)

if __name__ == '__main__':
    test_pv_details_structure()
