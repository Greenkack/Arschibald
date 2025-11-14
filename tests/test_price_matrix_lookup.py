"""test_price_matrix_lookup.py

Tests für die Preismatrix-Lookup-Logik.

Testet alle Funktionen des price_matrix_lookup Moduls:
- find_module_count_row: Modulanzahl-Suche mit Floor-Logik
- find_storage_column: Speichermodell-Suche
- lookup_price_by_intersection: Preis-Lookup an Kreuzung
- calculate_price_from_matrix: Haupt-Lookup-Funktion
"""

import price_matrix_store
import price_matrix_lookup


def test_find_module_count_row():
    """Test: Modulanzahl-Suche mit Floor-Logik"""
    print("\n=== Test: find_module_count_row ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix(
        name="Test Matrix - Module Count",
        description="Test für Modulanzahl-Suche"
    )
    
    if not matrix_id:
        print("[ERROR] Fehler: Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Zeilen hinzu (Modulanzahlen)
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    row_15 = price_matrix_store.add_row(matrix_id, "15")
    row_20 = price_matrix_store.add_row(matrix_id, "20")
    row_25 = price_matrix_store.add_row(matrix_id, "25")
    
    # Lade Matrix-Daten
    matrix_data = price_matrix_store.get_matrix_full(matrix_id)
    
    # Test 1: Exakte Übereinstimmung
    print("\nTest 1: Exakte Übereinstimmung")
    row_label, row_id = price_matrix_lookup.find_module_count_row(matrix_data, 20)
    if row_label == "20" and row_id == row_20:
        print(f"[OK] Exakte Übereinstimmung: {row_label} (ID: {row_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet '20' (ID: {row_20}), erhalten '{row_label}' (ID: {row_id})")
        return False
    
    # Test 2: Floor-Logik (18 -> 15)
    print("\nTest 2: Floor-Logik (18 -> 15)")
    row_label, row_id = price_matrix_lookup.find_module_count_row(matrix_data, 18)
    if row_label == "15" and row_id == row_15:
        print(f"[OK] Floor-Logik: {row_label} (ID: {row_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet '15' (ID: {row_15}), erhalten '{row_label}' (ID: {row_id})")
        return False
    
    # Test 3: Floor-Logik (23 -> 20)
    print("\nTest 3: Floor-Logik (23 -> 20)")
    row_label, row_id = price_matrix_lookup.find_module_count_row(matrix_data, 23)
    if row_label == "20" and row_id == row_20:
        print(f"[OK] Floor-Logik: {row_label} (ID: {row_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet '20' (ID: {row_20}), erhalten '{row_label}' (ID: {row_id})")
        return False
    
    # Test 4: Keine passende Zeile (zu klein)
    print("\nTest 4: Keine passende Zeile (zu klein)")
    row_label, row_id = price_matrix_lookup.find_module_count_row(matrix_data, 5)
    if row_label is None and row_id is None:
        print("[OK] Korrekt: Keine Zeile gefunden")
    else:
        print(f"[ERROR] Fehler: Erwartet None, erhalten '{row_label}' (ID: {row_id})")
        return False
    
    # Test 5: Größte Zahl (30 -> 25)
    print("\nTest 5: Größte Zahl (30 -> 25)")
    row_label, row_id = price_matrix_lookup.find_module_count_row(matrix_data, 30)
    if row_label == "25" and row_id == row_25:
        print(f"[OK] Floor-Logik: {row_label} (ID: {row_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet '25' (ID: {row_25}), erhalten '{row_label}' (ID: {row_id})")
        return False
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    print("\n[OK] Alle Tests für find_module_count_row bestanden")
    return True


def test_find_storage_column():
    """Test: Speichermodell-Suche"""
    print("\n=== Test: find_storage_column ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix(
        name="Test Matrix - Storage",
        description="Test für Speichermodell-Suche"
    )
    
    if not matrix_id:
        print("[ERROR] Fehler: Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Spalten hinzu (Speichermodelle)
    col_10kwh = price_matrix_store.add_column(matrix_id, "10kWh")
    col_15kwh = price_matrix_store.add_column(matrix_id, "15kWh")
    col_20kwh = price_matrix_store.add_column(matrix_id, "20kWh")
    col_none = price_matrix_store.add_column(matrix_id, "Kein Speicher")
    
    # Lade Matrix-Daten
    matrix_data = price_matrix_store.get_matrix_full(matrix_id)
    
    # Test 1: Exakte Übereinstimmung
    print("\nTest 1: Exakte Übereinstimmung")
    col_label, col_id = price_matrix_lookup.find_storage_column(matrix_data, "15kWh")
    if col_label == "15kWh" and col_id == col_15kwh:
        print(f"[OK] Exakte Übereinstimmung: {col_label} (ID: {col_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet '15kWh' (ID: {col_15kwh}), erhalten '{col_label}' (ID: {col_id})")
        return False
    
    # Test 2: Case-insensitive Suche
    print("\nTest 2: Case-insensitive Suche")
    col_label, col_id = price_matrix_lookup.find_storage_column(matrix_data, "10KWH")
    if col_label == "10kWh" and col_id == col_10kwh:
        print(f"[OK] Case-insensitive: {col_label} (ID: {col_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet '10kWh' (ID: {col_10kwh}), erhalten '{col_label}' (ID: {col_id})")
        return False
    
    # Test 3: None -> "Kein Speicher"
    print("\nTest 3: None -> 'Kein Speicher'")
    col_label, col_id = price_matrix_lookup.find_storage_column(matrix_data, None)
    if col_label == "Kein Speicher" and col_id == col_none:
        print(f"[OK] Kein Speicher: {col_label} (ID: {col_id})")
    else:
        print(f"[ERROR] Fehler: Erwartet 'Kein Speicher' (ID: {col_none}), erhalten '{col_label}' (ID: {col_id})")
        return False
    
    # Test 4: Nicht gefundenes Modell
    print("\nTest 4: Nicht gefundenes Modell")
    col_label, col_id = price_matrix_lookup.find_storage_column(matrix_data, "30kWh")
    if col_label is None and col_id is None:
        print("[OK] Korrekt: Keine Spalte gefunden")
    else:
        print(f"[ERROR] Fehler: Erwartet None, erhalten '{col_label}' (ID: {col_id})")
        return False
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    print("\n[OK] Alle Tests für find_storage_column bestanden")
    return True


def test_lookup_price_by_intersection():
    """Test: Preis-Lookup an Kreuzung"""
    print("\n=== Test: lookup_price_by_intersection ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix(
        name="Test Matrix - Price Lookup",
        description="Test für Preis-Lookup"
    )
    
    if not matrix_id:
        print("[ERROR] Fehler: Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Zeilen und Spalten hinzu
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    row_20 = price_matrix_store.add_row(matrix_id, "20")
    col_10kwh = price_matrix_store.add_column(matrix_id, "10kWh")
    col_15kwh = price_matrix_store.add_column(matrix_id, "15kWh")
    
    # Setze Preise
    price_matrix_store.set_cell_value(matrix_id, row_10, col_10kwh, 15000.0, "15000", "number")
    price_matrix_store.set_cell_value(matrix_id, row_10, col_15kwh, 17500.0, "17500", "number")
    price_matrix_store.set_cell_value(matrix_id, row_20, col_10kwh, 18000.0, "18000", "number")
    # row_20, col_15kwh bleibt leer
    
    # Lade Matrix-Daten
    matrix_data = price_matrix_store.get_matrix_full(matrix_id)
    
    # Test 1: Gültiger Preis
    print("\nTest 1: Gültiger Preis")
    price = price_matrix_lookup.lookup_price_by_intersection(matrix_data, row_10, col_10kwh)
    if price == 15000.0:
        print(f"[OK] Preis gefunden: {price}")
    else:
        print(f"[ERROR] Fehler: Erwartet 15000.0, erhalten {price}")
        return False
    
    # Test 2: Anderer gültiger Preis
    print("\nTest 2: Anderer gültiger Preis")
    price = price_matrix_lookup.lookup_price_by_intersection(matrix_data, row_20, col_10kwh)
    if price == 18000.0:
        print(f"[OK] Preis gefunden: {price}")
    else:
        print(f"[ERROR] Fehler: Erwartet 18000.0, erhalten {price}")
        return False
    
    # Test 3: Leere Zelle
    print("\nTest 3: Leere Zelle")
    price = price_matrix_lookup.lookup_price_by_intersection(matrix_data, row_20, col_15kwh)
    if price is None:
        print("[OK] Korrekt: Keine Preis-Zelle gefunden")
    else:
        print(f"[ERROR] Fehler: Erwartet None, erhalten {price}")
        return False
    
    # Test 4: Ungültige IDs
    print("\nTest 4: Ungültige IDs")
    price = price_matrix_lookup.lookup_price_by_intersection(matrix_data, 9999, 9999)
    if price is None:
        print("[OK] Korrekt: Keine Zelle für ungültige IDs")
    else:
        print(f"[ERROR] Fehler: Erwartet None, erhalten {price}")
        return False
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    print("\n[OK] Alle Tests für lookup_price_by_intersection bestanden")
    return True


def test_calculate_price_from_matrix():
    """Test: Haupt-Lookup-Funktion (End-to-End)"""
    print("\n=== Test: calculate_price_from_matrix ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix(
        name="Test Matrix - Complete",
        description="Test für vollständige Preisberechnung"
    )
    
    if not matrix_id:
        print("[ERROR] Fehler: Konnte Test-Matrix nicht erstellen")
        return False
    
    # Setze als aktive Matrix
    price_matrix_store.set_active_matrix(matrix_id)
    
    # Füge Zeilen hinzu (Modulanzahlen)
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    row_15 = price_matrix_store.add_row(matrix_id, "15")
    row_20 = price_matrix_store.add_row(matrix_id, "20")
    
    # Füge Spalten hinzu (Speichermodelle)
    col_10kwh = price_matrix_store.add_column(matrix_id, "10kWh")
    col_15kwh = price_matrix_store.add_column(matrix_id, "15kWh")
    col_none = price_matrix_store.add_column(matrix_id, "Kein Speicher")
    
    # Setze Preise
    price_matrix_store.set_cell_value(matrix_id, row_10, col_10kwh, 15000.0, "15000", "number")
    price_matrix_store.set_cell_value(matrix_id, row_10, col_15kwh, 17500.0, "17500", "number")
    price_matrix_store.set_cell_value(matrix_id, row_10, col_none, 12000.0, "12000", "number")
    price_matrix_store.set_cell_value(matrix_id, row_15, col_10kwh, 18000.0, "18000", "number")
    price_matrix_store.set_cell_value(matrix_id, row_15, col_15kwh, 20500.0, "20500", "number")
    price_matrix_store.set_cell_value(matrix_id, row_15, col_none, 15000.0, "15000", "number")
    price_matrix_store.set_cell_value(matrix_id, row_20, col_10kwh, 21000.0, "21000", "number")
    price_matrix_store.set_cell_value(matrix_id, row_20, col_15kwh, 23500.0, "23500", "number")
    price_matrix_store.set_cell_value(matrix_id, row_20, col_none, 18000.0, "18000", "number")
    
    # Test 1: Exakte Übereinstimmung
    print("\nTest 1: Exakte Übereinstimmung (20 Module, 15kWh)")
    result = price_matrix_lookup.calculate_price_from_matrix(20, "15kWh")
    if result['success'] and result['base_price'] == 23500.0:
        print(f"[OK] Preis: {result['base_price']} EUR")
        print(f"  Zeile: {result['row_used']}, Spalte: {result['column_used']}")
    else:
        print(f"[ERROR] Fehler: {result.get('error', 'Unbekannter Fehler')}")
        return False
    
    # Test 2: Floor-Logik (18 Module -> 15)
    print("\nTest 2: Floor-Logik (18 Module -> 15, 10kWh)")
    result = price_matrix_lookup.calculate_price_from_matrix(18, "10kWh")
    if result['success'] and result['base_price'] == 18000.0 and result['row_used'] == "15":
        print(f"[OK] Preis: {result['base_price']} EUR")
        print(f"  Zeile: {result['row_used']} (Floor von 18), Spalte: {result['column_used']}")
    else:
        print(f"[ERROR] Fehler: {result.get('error', 'Unbekannter Fehler')}")
        return False
    
    # Test 3: Kein Speicher (None)
    print("\nTest 3: Kein Speicher (10 Module, None)")
    result = price_matrix_lookup.calculate_price_from_matrix(10, None)
    if result['success'] and result['base_price'] == 12000.0 and result['column_used'] == "Kein Speicher":
        print(f"[OK] Preis: {result['base_price']} EUR")
        print(f"  Zeile: {result['row_used']}, Spalte: {result['column_used']}")
    else:
        print(f"[ERROR] Fehler: {result.get('error', 'Unbekannter Fehler')}")
        return False
    
    # Test 4: Modulanzahl zu klein
    print("\nTest 4: Modulanzahl zu klein (5 Module)")
    result = price_matrix_lookup.calculate_price_from_matrix(5, "10kWh")
    if not result['success'] and result['error_type'] == 'no_row':
        print(f"[OK] Korrekt: {result['error']}")
    else:
        print(f"[ERROR] Fehler: Erwarteter Fehlertyp 'no_row', erhalten '{result.get('error_type')}'")
        return False
    
    # Test 5: Speichermodell nicht gefunden
    print("\nTest 5: Speichermodell nicht gefunden (30kWh)")
    result = price_matrix_lookup.calculate_price_from_matrix(20, "30kWh")
    if not result['success'] and result['error_type'] == 'no_column':
        print(f"[OK] Korrekt: {result['error']}")
    else:
        print(f"[ERROR] Fehler: Erwarteter Fehlertyp 'no_column', erhalten '{result.get('error_type')}'")
        return False
    
    # Test 6: Matrix-ID explizit angeben
    print("\nTest 6: Matrix-ID explizit angeben")
    result = price_matrix_lookup.calculate_price_from_matrix(15, "15kWh", matrix_id=matrix_id)
    if result['success'] and result['base_price'] == 20500.0:
        print(f"[OK] Preis: {result['base_price']} EUR")
        print(f"  Matrix: {result['matrix_name']} (ID: {result['matrix_id']})")
    else:
        print(f"[ERROR] Fehler: {result.get('error', 'Unbekannter Fehler')}")
        return False
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    print("\n[OK] Alle Tests für calculate_price_from_matrix bestanden")
    return True


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 60)
    print("PREISMATRIX-LOOKUP TESTS")
    print("=" * 60)
    
    tests = [
        ("Modulanzahl-Suche", test_find_module_count_row),
        ("Speichermodell-Suche", test_find_storage_column),
        ("Preis-Lookup", test_lookup_price_by_intersection),
        ("Haupt-Lookup-Funktion", test_calculate_price_from_matrix)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n[ERROR] Exception in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    
    for name, success in results:
        status = "[OK] BESTANDEN" if success else "[ERROR] FEHLGESCHLAGEN"
        print(f"{name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[OK] ALLE TESTS BESTANDEN")
    else:
        print("[ERROR] EINIGE TESTS FEHLGESCHLAGEN")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
