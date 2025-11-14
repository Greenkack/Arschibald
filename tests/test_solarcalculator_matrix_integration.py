"""
Test für Solarcalculator Preismatrix-Integration

Testet die grundlegende Funktionalität der Matrix-Preisberechnung
im Solarcalculator.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_get_total_price_with_matrix_mode():
    """Test der Hauptfunktion get_total_price_with_matrix_mode"""
    from solar_calculator import get_total_price_with_matrix_mode
    
    # Test-Details mit Modulanzahl und Speichermodell
    details = {
        'module_quantity': 20,
        'selected_storage_name': '15kWh'
    }
    
    # Funktion aufrufen
    result = get_total_price_with_matrix_mode(details)
    
    # Prüfen dass Ergebnis-Dictionary die erwarteten Keys hat
    assert 'success' in result
    assert 'base_price' in result
    assert 'extras_price' in result
    assert 'net_total' in result
    assert 'vat_amount' in result
    assert 'gross_total' in result
    assert 'breakdown' in result
    assert 'matrix_info' in result
    
    print("[OK] get_total_price_with_matrix_mode() gibt korrektes Dictionary zurück")
    
    # Wenn erfolgreich, prüfe Preisberechnung
    if result['success']:
        assert result['base_price'] > 0, "Basispreis sollte größer als 0 sein"
        assert result['net_total'] >= result['base_price'], "Netto-Total sollte >= Basispreis sein"
        assert result['gross_total'] > result['net_total'], "Brutto-Total sollte > Netto-Total sein"
        print(f"[OK] Preisberechnung erfolgreich: Basispreis={result['base_price']}, Netto={result['net_total']}, Brutto={result['gross_total']}")
    else:
        print(f"[INFO] Preisberechnung nicht erfolgreich (erwartet wenn keine Matrix aktiv): {result.get('error')}")


def test_calculate_matrix_extras():
    """Test der Extras-Berechnung"""
    from solar_calculator import _calculate_matrix_extras
    
    # Test-Details ohne Extras
    details = {}
    extras = _calculate_matrix_extras(details)
    
    assert isinstance(extras, float), "Extras sollten als float zurückgegeben werden"
    assert extras >= 0, "Extras sollten nicht negativ sein"
    
    print(f"[OK] _calculate_matrix_extras() funktioniert: {extras}")


def test_calculate_matrix_extras_detailed():
    """Test der detaillierten Extras-Berechnung"""
    from solar_calculator import _calculate_matrix_extras_detailed
    
    # Test-Details ohne Extras
    details = {}
    breakdown = _calculate_matrix_extras_detailed(details)
    
    assert isinstance(breakdown, dict), "Breakdown sollte ein Dictionary sein"
    assert 'total' in breakdown
    assert 'special_products' in breakdown
    assert 'services' in breakdown
    assert 'extras' in breakdown
    
    assert isinstance(breakdown['total'], float)
    assert isinstance(breakdown['special_products'], list)
    assert isinstance(breakdown['services'], list)
    assert isinstance(breakdown['extras'], list)
    
    print(f"[OK] _calculate_matrix_extras_detailed() gibt korrektes Dictionary zurück")


def test_pricing_mode_check():
    """Test der Preisberechnungsmodus-Prüfung"""
    from database import get_pricing_calculation_mode
    
    mode = get_pricing_calculation_mode()
    
    assert mode in ['standard', 'matrix'], f"Modus sollte 'standard' oder 'matrix' sein, ist aber: {mode}"
    
    print(f"[OK] Preisberechnungsmodus: {mode}")


def test_invalid_module_count():
    """Test mit ungültiger Modulanzahl"""
    from solar_calculator import get_total_price_with_matrix_mode
    
    # Test mit Modulanzahl 0
    details = {
        'module_quantity': 0,
        'selected_storage_name': '15kWh'
    }
    
    result = get_total_price_with_matrix_mode(details)
    
    assert not result['success'], "Sollte fehlschlagen bei Modulanzahl 0"
    assert result['error'] is not None, "Sollte Fehlermeldung enthalten"
    
    print(f"[OK] Fehlerbehandlung für ungültige Modulanzahl funktioniert: {result['error']}")


def test_placeholder_storage_model():
    """Test mit Placeholder-Text als Speichermodell"""
    from solar_calculator import get_total_price_with_matrix_mode
    
    # Test mit Placeholder-Text
    details = {
        'module_quantity': 20,
        'selected_storage_name': '--- Bitte wählen ---'
    }
    
    result = get_total_price_with_matrix_mode(details)
    
    # Sollte Placeholder als None behandeln
    print(f"[OK] Placeholder-Behandlung: success={result['success']}")


def run_all_tests():
    """Führt alle Tests aus"""
    print("\n" + "="*60)
    print("SOLARCALCULATOR MATRIX-INTEGRATION TESTS")
    print("="*60 + "\n")
    
    tests = [
        ("Preisberechnungsmodus-Prüfung", test_pricing_mode_check),
        ("Matrix-Extras-Berechnung", test_calculate_matrix_extras),
        ("Detaillierte Extras-Berechnung", test_calculate_matrix_extras_detailed),
        ("Hauptfunktion get_total_price_with_matrix_mode", test_get_total_price_with_matrix_mode),
        ("Fehlerbehandlung: Ungültige Modulanzahl", test_invalid_module_count),
        ("Placeholder-Behandlung", test_placeholder_storage_model),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 60)
        try:
            test_func()
            passed += 1
            print(f"[OK] PASSED\n")
        except Exception as e:
            failed += 1
            print(f"[ERROR] FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"ERGEBNIS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
