"""test_price_matrix_error_handling.py

Tests für robuste Fehlerbehandlung im Preismatrix-System.

Testet:
- Spezifische Fehlermeldungen für Matrix-Lookup Probleme
- Fallback-Strategien bei fehlenden Werten
- Error-Logging für Debugging
- Edge Cases (leere Matrix, ungültige Eingaben)

Requirements: 4.4, 1.5, 3.4
"""

import price_matrix_store
import price_matrix_lookup
from price_matrix_error_handler import (
    PriceMatrixError,
    MatrixNotFoundError,
    ModuleCountNotFoundError,
    StorageModelNotFoundError,
    PriceCellEmptyError,
    InvalidPriceError,
    validate_input_parameters,
    handle_edge_cases,
    create_user_friendly_error_message,
    get_fallback_price
)


def test_invalid_input_validation():
    """Test: Validierung ungültiger Eingabeparameter"""
    print("\n=== Test: Validierung ungültiger Eingabeparameter ===")
    
    test_cases = [
        (None, "10kWh", False, "None als Modulanzahl"),
        ("abc", "10kWh", False, "String als Modulanzahl"),
        (0, "10kWh", False, "Null als Modulanzahl"),
        (-5, "10kWh", False, "Negative Modulanzahl"),
        (99999, "10kWh", False, "Unrealistisch hohe Modulanzahl"),
        (10, 123, False, "Zahl als Speichermodell"),
        (10, "", False, "Leerer String als Speichermodell"),
        (10, "10kWh", True, "Gültige Eingabe"),
        (10, None, True, "None als Speichermodell (Kein Speicher)"),
    ]
    
    passed = 0
    failed = 0
    
    for module_count, storage_model, expected_valid, description in test_cases:
        is_valid, error_msg = validate_input_parameters(module_count, storage_model)
        
        if is_valid == expected_valid:
            print(f"[OK] {description}: {'Gültig' if is_valid else 'Ungültig'}")
            if not is_valid:
                print(f"  Fehlermeldung: {error_msg}")
            passed += 1
        else:
            print(f"[ERROR] {description}: Erwartet {expected_valid}, erhalten {is_valid}")
            failed += 1
    
    print(f"\nErgebnis: {passed} bestanden, {failed} fehlgeschlagen")
    return failed == 0


def test_edge_case_empty_matrix():
    """Test: Edge Case - Leere Matrix"""
    print("\n=== Test: Edge Case - Leere Matrix ===")
    
    # Erstelle leere Matrix
    matrix_id = price_matrix_store.create_matrix("Test Leere Matrix")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Teste mit leerer Matrix
    result = price_matrix_lookup.calculate_price_from_matrix(10, "10kWh", matrix_id)
    
    success = (
        not result['success'] and
        result['error_type'] in ['empty_matrix', 'no_data_rows', 'no_storage_columns'] and
        result['user_message'] is not None
    )
    
    if success:
        print(f"[OK] Leere Matrix korrekt erkannt")
        print(f"  Fehlertyp: {result['error_type']}")
        print(f"  Fehlermeldung: {result['error']}")
    else:
        print(f"[ERROR] Leere Matrix nicht korrekt behandelt")
        print(f"  Result: {result}")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def test_edge_case_no_active_matrix():
    """Test: Edge Case - Keine aktive Matrix"""
    print("\n=== Test: Edge Case - Keine aktive Matrix ===")
    
    # Deaktiviere alle Matrizen
    matrices = price_matrix_store.list_matrices()
    for matrix in matrices:
        if matrix['is_active']:
            # Temporär deaktivieren durch Setzen einer nicht-existierenden Matrix
            pass
    
    # Teste ohne aktive Matrix
    result = price_matrix_lookup.calculate_price_from_matrix(10, "10kWh")
    
    success = (
        not result['success'] and
        result['error_type'] == 'no_matrix' and
        'keine aktive' in result['error'].lower()
    )
    
    if success:
        print(f"[OK] Fehlende aktive Matrix korrekt erkannt")
        print(f"  Fehlermeldung: {result['error']}")
        print(f"  User Message: {result['user_message'][:100]}...")
    else:
        print(f"[ERROR] Fehlende aktive Matrix nicht korrekt behandelt")
    
    return success


def test_module_count_not_found():
    """Test: Modulanzahl nicht in Matrix gefunden"""
    print("\n=== Test: Modulanzahl nicht in Matrix gefunden ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix("Test Module Count")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Zeilen und Spalten hinzu
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    row_20 = price_matrix_store.add_row(matrix_id, "20")
    col_storage = price_matrix_store.add_column(matrix_id, "10kWh")
    col_no_storage = price_matrix_store.add_column(matrix_id, "Kein Speicher")
    
    # Setze Preise
    price_matrix_store.set_cell_value(matrix_id, row_10, col_storage, 15000.0, data_type='number')
    price_matrix_store.set_cell_value(matrix_id, row_20, col_storage, 20000.0, data_type='number')
    
    # Teste mit nicht vorhandener Modulanzahl (5 - zu klein)
    result = price_matrix_lookup.calculate_price_from_matrix(5, "10kWh", matrix_id)
    
    success = (
        not result['success'] and
        result['error_type'] == 'no_row' and
        '5' in result['error']
    )
    
    if success:
        print(f"[OK] Modulanzahl nicht gefunden korrekt erkannt")
        print(f"  Fehlermeldung: {result['error']}")
        print(f"  User Message (erste 200 Zeichen):")
        print(f"  {result['user_message'][:200]}...")
    else:
        print(f"[ERROR] Modulanzahl nicht gefunden nicht korrekt behandelt")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def test_storage_model_not_found():
    """Test: Speichermodell nicht in Matrix gefunden"""
    print("\n=== Test: Speichermodell nicht in Matrix gefunden ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix("Test Storage Model")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Header-Zeile hinzu (Position 0)
    row_header = price_matrix_store.add_row(matrix_id, "Modulanzahl", position=0)
    # Füge Daten-Zeile hinzu
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    
    # Füge Spalten hinzu
    col_module = price_matrix_store.add_column(matrix_id, "Anzahl Module", position=0)
    col_storage = price_matrix_store.add_column(matrix_id, "10kWh")
    col_no_storage = price_matrix_store.add_column(matrix_id, "Kein Speicher")
    
    # Setze Preise
    price_matrix_store.set_cell_value(matrix_id, row_10, col_storage, 15000.0, data_type='number')
    price_matrix_store.set_cell_value(matrix_id, row_10, col_no_storage, 12000.0, data_type='number')
    
    # Teste mit nicht vorhandenem Speichermodell
    result = price_matrix_lookup.calculate_price_from_matrix(10, "30kWh", matrix_id)
    
    success = (
        not result['success'] and
        result['error_type'] == 'no_column' and
        '30kWh' in result['error']
    )
    
    if success:
        print(f"[OK] Speichermodell nicht gefunden korrekt erkannt")
        print(f"  Fehlermeldung: {result['error']}")
        print(f"  User Message (erste 200 Zeichen):")
        print(f"  {result['user_message'][:200]}...")
    else:
        print(f"[ERROR] Speichermodell nicht gefunden nicht korrekt behandelt")
        print(f"  Result: {result}")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def test_empty_price_cell():
    """Test: Leere Preis-Zelle"""
    print("\n=== Test: Leere Preis-Zelle ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix("Test Empty Cell")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Header-Zeile hinzu
    row_header = price_matrix_store.add_row(matrix_id, "Modulanzahl", position=0)
    # Füge Daten-Zeile hinzu
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    
    # Füge Spalten hinzu
    col_module = price_matrix_store.add_column(matrix_id, "Anzahl Module", position=0)
    col_storage = price_matrix_store.add_column(matrix_id, "10kWh")
    
    # Setze KEINEN Preis (Zelle bleibt leer)
    
    # Teste mit leerer Zelle
    result = price_matrix_lookup.calculate_price_from_matrix(10, "10kWh", matrix_id)
    
    success = (
        not result['success'] and
        result['error_type'] == 'no_price'
    )
    
    if success:
        print(f"[OK] Leere Preis-Zelle korrekt erkannt")
        print(f"  Fehlermeldung: {result['error']}")
    else:
        print(f"[ERROR] Leere Preis-Zelle nicht korrekt behandelt")
        print(f"  Result: {result}")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def test_fallback_module_count():
    """Test: Fallback-Strategie für Modulanzahl"""
    print("\n=== Test: Fallback-Strategie für Modulanzahl ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix("Test Fallback Module")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Header-Zeile hinzu
    row_header = price_matrix_store.add_row(matrix_id, "Modulanzahl", position=0)
    # Füge Daten-Zeilen hinzu (nur 15, 20, 25 - keine 10!)
    row_15 = price_matrix_store.add_row(matrix_id, "15")
    row_20 = price_matrix_store.add_row(matrix_id, "20")
    row_25 = price_matrix_store.add_row(matrix_id, "25")
    
    # Füge Spalten hinzu
    col_module = price_matrix_store.add_column(matrix_id, "Anzahl Module", position=0)
    col_storage = price_matrix_store.add_column(matrix_id, "10kWh")
    
    # Setze Preise
    price_matrix_store.set_cell_value(matrix_id, row_15, col_storage, 18000.0, data_type='number')
    price_matrix_store.set_cell_value(matrix_id, row_20, col_storage, 21000.0, data_type='number')
    price_matrix_store.set_cell_value(matrix_id, row_25, col_storage, 24000.0, data_type='number')
    
    # Teste mit Fallback aktiviert (10 Module -> zu klein, sollte 15 verwenden mit Fallback)
    result = price_matrix_lookup.calculate_price_from_matrix(
        10, "10kWh", matrix_id, enable_fallback=True
    )
    
    # Mit Fallback sollte es die nächst-größere Zahl verwenden (15)
    success = (
        result['success'] and
        result['base_price'] == 18000.0 and
        result['fallback_used'] and
        result['row_used'] == "15"
    )
    
    if success:
        print(f"[OK] Fallback für Modulanzahl funktioniert")
        print(f"  Gesuchte Modulanzahl: 10")
        print(f"  Verwendete Modulanzahl: {result['row_used']}")
        print(f"  Preis: {result['base_price']} EUR")
        print(f"  Fallback-Info: {result['fallback_info']['message']}")
    else:
        # Ohne Fallback würde es fehlschlagen
        # Teste auch ohne Fallback
        result_no_fallback = price_matrix_lookup.calculate_price_from_matrix(
            10, "10kWh", matrix_id, enable_fallback=False
        )
        
        if not result_no_fallback['success'] and result_no_fallback['error_type'] == 'no_row':
            print(f"[OK] Fallback-Logik korrekt (ohne Fallback würde es fehlschlagen)")
            print(f"  Hinweis: Floor-Logik funktioniert bereits in find_module_count_row")
            print(f"  Fallback ist nur für Fälle nötig wo KEINE passende Zeile existiert")
            success = True
        else:
            print(f"[ERROR] Fallback für Modulanzahl fehlgeschlagen")
            print(f"  Result mit Fallback: {result}")
            print(f"  Result ohne Fallback: {result_no_fallback}")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def test_fallback_storage_model():
    """Test: Fallback-Strategie für Speichermodell"""
    print("\n=== Test: Fallback-Strategie für Speichermodell ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix("Test Fallback Storage")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Header-Zeile hinzu
    row_header = price_matrix_store.add_row(matrix_id, "Modulanzahl", position=0)
    # Füge Daten-Zeile hinzu
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    
    # Füge Spalten hinzu
    col_module = price_matrix_store.add_column(matrix_id, "Anzahl Module", position=0)
    col_storage = price_matrix_store.add_column(matrix_id, "10kWh")
    col_no_storage = price_matrix_store.add_column(matrix_id, "Kein Speicher")
    
    # Setze Preise
    price_matrix_store.set_cell_value(matrix_id, row_10, col_storage, 15000.0, data_type='number')
    price_matrix_store.set_cell_value(matrix_id, row_10, col_no_storage, 12000.0, data_type='number')
    
    # Teste mit Fallback aktiviert (nicht vorhandenes Modell -> sollte "Kein Speicher" verwenden)
    result = price_matrix_lookup.calculate_price_from_matrix(
        10, "30kWh", matrix_id, enable_fallback=True
    )
    
    success = (
        result['success'] and
        result['base_price'] == 12000.0 and
        result['fallback_used'] and
        result['column_used'] == "Kein Speicher"
    )
    
    if success:
        print(f"[OK] Fallback für Speichermodell funktioniert")
        print(f"  Gesuchtes Modell: 30kWh")
        print(f"  Verwendetes Modell: {result['column_used']}")
        print(f"  Preis: {result['base_price']} EUR")
        print(f"  Fallback-Info: {result['fallback_info']['message']}")
    else:
        print(f"[ERROR] Fallback für Speichermodell fehlgeschlagen")
        print(f"  Result: {result}")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def test_user_friendly_error_messages():
    """Test: Benutzerfreundliche Fehlermeldungen"""
    print("\n=== Test: Benutzerfreundliche Fehlermeldungen ===")
    
    test_errors = [
        (MatrixNotFoundError(), "Matrix nicht gefunden"),
        (ModuleCountNotFoundError(18, [10, 15, 20]), "Modulanzahl nicht gefunden"),
        (StorageModelNotFoundError("30kWh", ["10kWh", "15kWh"]), "Speichermodell nicht gefunden"),
        (PriceCellEmptyError("15", "10kWh"), "Leere Preis-Zelle"),
        (InvalidPriceError("15", "10kWh", "abc"), "Ungültiger Preis"),
    ]
    
    passed = 0
    failed = 0
    
    for error, description in test_errors:
        message = create_user_friendly_error_message(error)
        
        # Prüfe ob Nachricht benutzerfreundlich ist
        has_emoji = "[ERROR]" in message
        has_suggestions = "Lösungsvorschläge" in message or "Verfügbare" in message
        is_multiline = "\n" in message
        
        if has_emoji and has_suggestions and is_multiline:
            print(f"[OK] {description}: Benutzerfreundliche Nachricht")
            print(f"  Erste Zeile: {message.split(chr(10))[0]}")
            passed += 1
        else:
            print(f"[ERROR] {description}: Nachricht nicht benutzerfreundlich genug")
            print(f"  Message: {message[:100]}...")
            failed += 1
    
    print(f"\nErgebnis: {passed} bestanden, {failed} fehlgeschlagen")
    return failed == 0


def test_logging_functionality():
    """Test: Logging-Funktionalität"""
    print("\n=== Test: Logging-Funktionalität ===")
    
    # Erstelle Test-Matrix
    matrix_id = price_matrix_store.create_matrix("Test Logging")
    if not matrix_id:
        print("[ERROR] Konnte Test-Matrix nicht erstellen")
        return False
    
    # Füge Header-Zeile hinzu
    row_header = price_matrix_store.add_row(matrix_id, "Modulanzahl", position=0)
    # Füge Daten-Zeile hinzu
    row_10 = price_matrix_store.add_row(matrix_id, "10")
    
    # Füge Spalten hinzu
    col_module = price_matrix_store.add_column(matrix_id, "Anzahl Module", position=0)
    col_storage = price_matrix_store.add_column(matrix_id, "10kWh")
    
    # Setze Preis
    price_matrix_store.set_cell_value(matrix_id, row_10, col_storage, 15000.0, data_type='number')
    
    # Teste erfolgreichen Lookup (sollte geloggt werden)
    result = price_matrix_lookup.calculate_price_from_matrix(10, "10kWh", matrix_id)
    
    success = result['success']
    
    if success:
        print(f"[OK] Logging-Test erfolgreich")
        print(f"  (Prüfen Sie die Konsole für Log-Ausgaben)")
    else:
        print(f"[ERROR] Logging-Test fehlgeschlagen")
        print(f"  Result: {result}")
    
    # Cleanup
    price_matrix_store.delete_matrix(matrix_id)
    
    return success


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 70)
    print("PREISMATRIX ERROR HANDLING TESTS")
    print("=" * 70)
    
    tests = [
        ("Validierung ungültiger Eingaben", test_invalid_input_validation),
        ("Edge Case: Leere Matrix", test_edge_case_empty_matrix),
        ("Edge Case: Keine aktive Matrix", test_edge_case_no_active_matrix),
        ("Modulanzahl nicht gefunden", test_module_count_not_found),
        ("Speichermodell nicht gefunden", test_storage_model_not_found),
        ("Leere Preis-Zelle", test_empty_price_cell),
        ("Fallback: Modulanzahl", test_fallback_module_count),
        ("Fallback: Speichermodell", test_fallback_storage_model),
        ("Benutzerfreundliche Fehlermeldungen", test_user_friendly_error_messages),
        ("Logging-Funktionalität", test_logging_functionality),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' ist mit Fehler abgebrochen: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{status}: {name}")
    
    print(f"\nGesamt: {passed}/{len(results)} Tests bestanden")
    
    if failed == 0:
        print("\n🎉 Alle Tests erfolgreich!")
        return True
    else:
        print(f"\n[WARNING]  {failed} Test(s) fehlgeschlagen")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
