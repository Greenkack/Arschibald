"""
Test für Dachtyp-Erkennung Fix

Dieser Test verifiziert, dass die Dachtyp-Erkennung korrekt funktioniert
und "Satteldach" nicht als "Flachdach" erkannt wird.
"""

def test_is_flat_roof():
    """Test dass is_flat_roof nur Flachdächer erkennt"""
    from utils.pv3d_mounting_logic import is_flat_roof
    
    print("\n=== Test: is_flat_roof Funktion ===")
    
    # Test 1: Flachdach sollte erkannt werden
    assert is_flat_roof("Flachdach") == True, "Flachdach sollte erkannt werden"
    print("[OK] 'Flachdach' wird als Flachdach erkannt")
    
    # Test 2: Satteldach sollte NICHT als Flachdach erkannt werden
    assert is_flat_roof("Satteldach") == False, "Satteldach sollte NICHT als Flachdach erkannt werden"
    print("[OK] 'Satteldach' wird NICHT als Flachdach erkannt")
    
    # Test 3: Pultdach sollte NICHT als Flachdach erkannt werden
    assert is_flat_roof("Pultdach") == False, "Pultdach sollte NICHT als Flachdach erkannt werden"
    print("[OK] 'Pultdach' wird NICHT als Flachdach erkannt")
    
    # Test 4: Walmdach sollte NICHT als Flachdach erkannt werden
    assert is_flat_roof("Walmdach") == False, "Walmdach sollte NICHT als Flachdach erkannt werden"
    print("[OK] 'Walmdach' wird NICHT als Flachdach erkannt")
    
    # Test 5: Zeltdach sollte NICHT als Flachdach erkannt werden
    assert is_flat_roof("Zeltdach") == False, "Zeltdach sollte NICHT als Flachdach erkannt werden"
    print("[OK] 'Zeltdach' wird NICHT als Flachdach erkannt")
    
    print("\n[OK] Alle Tests bestanden!")


def test_is_pitched_roof():
    """Test dass is_pitched_roof nur Schrägdächer erkennt"""
    from utils.pv3d_mounting_logic import is_pitched_roof
    
    print("\n=== Test: is_pitched_roof Funktion ===")
    
    # Test 1: Satteldach sollte als Schrägdach erkannt werden
    assert is_pitched_roof("Satteldach") == True, "Satteldach sollte als Schrägdach erkannt werden"
    print("[OK] 'Satteldach' wird als Schrägdach erkannt")
    
    # Test 2: Pultdach sollte als Schrägdach erkannt werden
    assert is_pitched_roof("Pultdach") == True, "Pultdach sollte als Schrägdach erkannt werden"
    print("[OK] 'Pultdach' wird als Schrägdach erkannt")
    
    # Test 3: Walmdach sollte als Schrägdach erkannt werden
    assert is_pitched_roof("Walmdach") == True, "Walmdach sollte als Schrägdach erkannt werden"
    print("[OK] 'Walmdach' wird als Schrägdach erkannt")
    
    # Test 4: Flachdach sollte NICHT als Schrägdach erkannt werden
    assert is_pitched_roof("Flachdach") == False, "Flachdach sollte NICHT als Schrägdach erkannt werden"
    print("[OK] 'Flachdach' wird NICHT als Schrägdach erkannt")
    
    print("\n[OK] Alle Tests bestanden!")


def test_get_allowed_mounting_types():
    """Test dass die richtigen Montagetypen für jeden Dachtyp zurückgegeben werden"""
    from utils.pv3d_mounting_logic import get_allowed_mounting_types
    
    print("\n=== Test: get_allowed_mounting_types Funktion ===")
    
    # Test 1: Flachdach sollte Aufständerungen erlauben
    flat_types = get_allowed_mounting_types("Flachdach")
    assert "Aufständerung Süd" in flat_types, "Flachdach sollte Aufständerung Süd erlauben"
    assert "Aufständerung Ost-West" in flat_types, "Flachdach sollte Aufständerung Ost-West erlauben"
    print(f"[OK] Flachdach erlaubt: {flat_types}")
    
    # Test 2: Satteldach sollte nur Aufdach-Montage erlauben
    pitched_types = get_allowed_mounting_types("Satteldach")
    assert "Aufdach-Montage" in pitched_types, "Satteldach sollte Aufdach-Montage erlauben"
    assert "Aufständerung Süd" not in pitched_types, "Satteldach sollte KEINE Aufständerung erlauben"
    print(f"[OK] Satteldach erlaubt: {pitched_types}")
    
    # Test 3: Pultdach sollte nur Aufdach-Montage erlauben
    pult_types = get_allowed_mounting_types("Pultdach")
    assert "Aufdach-Montage" in pult_types, "Pultdach sollte Aufdach-Montage erlauben"
    assert "Aufständerung Süd" not in pult_types, "Pultdach sollte KEINE Aufständerung erlauben"
    print(f"[OK] Pultdach erlaubt: {pult_types}")
    
    print("\n[OK] Alle Tests bestanden!")


if __name__ == "__main__":
    print("=" * 70)
    print("DACHTYP-ERKENNUNG FIX - TEST SUITE")
    print("=" * 70)
    
    try:
        test_is_flat_roof()
        test_is_pitched_roof()
        test_get_allowed_mounting_types()
        
        print("\n" + "=" * 70)
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("=" * 70)
        print("\nDas Problem ist behoben:")
        print("- Satteldach wird korrekt als Schrägdach erkannt")
        print("- Flachdach wird korrekt als Flachdach erkannt")
        print("- Montagetypen werden korrekt zugewiesen")
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
