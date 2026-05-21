"""
Test für Preisberechnungsmodus-Funktionen in database.py

Testet:
- get_pricing_calculation_mode()
- set_pricing_calculation_mode()
- Default-Wert
- Validierung
"""

import sys
import os

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    get_pricing_calculation_mode,
    set_pricing_calculation_mode,
    save_admin_setting,
    load_admin_setting
)


def test_default_mode():
    """Test: Default-Modus ist 'standard'"""
    print("\n=== Test 1: Default-Modus ===")
    
    # Lösche eventuell vorhandenen Wert
    save_admin_setting('pricing_calculation_mode', None)
    
    mode = get_pricing_calculation_mode()
    print(f"Default-Modus: {mode}")
    
    assert mode == 'standard', f"Erwartet 'standard', erhalten '{mode}'"
    print("Default-Modus ist 'standard'")


def test_set_standard_mode():
    """Test: Setzen auf 'standard' Modus"""
    print("\n=== Test 2: Standard-Modus setzen ===")
    
    success = set_pricing_calculation_mode('standard')
    print(f"Setzen erfolgreich: {success}")
    
    assert success, "Setzen sollte erfolgreich sein"
    
    mode = get_pricing_calculation_mode()
    print(f"Geladener Modus: {mode}")
    
    assert mode == 'standard', f"Erwartet 'standard', erhalten '{mode}'"
    print("Standard-Modus erfolgreich gesetzt und geladen")


def test_set_matrix_mode():
    """Test: Setzen auf 'matrix' Modus"""
    print("\n=== Test 3: Matrix-Modus setzen ===")
    
    success = set_pricing_calculation_mode('matrix')
    print(f"Setzen erfolgreich: {success}")
    
    assert success, "Setzen sollte erfolgreich sein"
    
    mode = get_pricing_calculation_mode()
    print(f"Geladener Modus: {mode}")
    
    assert mode == 'matrix', f"Erwartet 'matrix', erhalten '{mode}'"
    print("Matrix-Modus erfolgreich gesetzt und geladen")


def test_invalid_mode():
    """Test: Ungültiger Modus wird abgelehnt"""
    print("\n=== Test 4: Ungültiger Modus ===")
    
    # Setze zuerst auf bekannten Wert
    set_pricing_calculation_mode('standard')
    
    # Versuche ungültigen Modus zu setzen
    success = set_pricing_calculation_mode('invalid')
    print(f"Setzen erfolgreich: {success}")
    
    assert not success, "Setzen sollte fehlschlagen"
    
    # Modus sollte unverändert sein
    mode = get_pricing_calculation_mode()
    print(f"Modus nach ungültigem Versuch: {mode}")
    
    assert mode == 'standard', f"Modus sollte unverändert 'standard' sein, ist aber '{mode}'"
    print("Ungültiger Modus wurde korrekt abgelehnt")


def test_mode_persistence():
    """Test: Modus bleibt über mehrere Aufrufe erhalten"""
    print("\n=== Test 5: Persistenz ===")
    
    # Setze auf Matrix
    set_pricing_calculation_mode('matrix')
    mode1 = get_pricing_calculation_mode()
    print(f"Modus nach Setzen: {mode1}")
    
    # Lade erneut
    mode2 = get_pricing_calculation_mode()
    print(f"Modus nach erneutem Laden: {mode2}")
    
    assert mode1 == mode2 == 'matrix', "Modus sollte persistent sein"
    print("Modus bleibt persistent")
    
    # Zurück auf Standard
    set_pricing_calculation_mode('standard')
    mode3 = get_pricing_calculation_mode()
    print(f"Modus nach Zurücksetzen: {mode3}")
    
    assert mode3 == 'standard', "Modus sollte auf 'standard' zurückgesetzt sein"
    print("Modus kann erfolgreich geändert werden")


def test_corrupted_value_handling():
    """Test: Umgang mit korrupten Werten in Datenbank"""
    print("\n=== Test 6: Korrupte Werte ===")
    
    # Setze manuell einen ungültigen Wert
    save_admin_setting('pricing_calculation_mode', 'corrupted_value')
    
    # Sollte auf 'standard' zurückfallen
    mode = get_pricing_calculation_mode()
    print(f"Modus bei korruptem Wert: {mode}")
    
    assert mode == 'standard', f"Sollte auf 'standard' zurückfallen, ist aber '{mode}'"
    print("Korrupte Werte werden korrekt behandelt")
    
    # Aufräumen
    set_pricing_calculation_mode('standard')


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 60)
    print("PREISBERECHNUNGSMODUS - TESTS")
    print("=" * 60)
    
    tests = [
        test_default_mode,
        test_set_standard_mode,
        test_set_matrix_mode,
        test_invalid_mode,
        test_mode_persistence,
        test_corrupted_value_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"Test fehlgeschlagen: {e}")
            failed += 1
        except Exception as e:
            print(f"Test-Fehler: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"ERGEBNIS: {passed} Tests bestanden, {failed} Tests fehlgeschlagen")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
