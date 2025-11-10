"""
Test für Montagetyp-Validierung Fix

Testet dass die Validierung korrekt funktioniert und keine falschen Warnungen anzeigt.
"""

def test_mounting_validation():
    """Test dass Validierung korrekt funktioniert"""
    from utils.pv3d_mounting_logic import (
        validate_mounting_selection,
        get_allowed_mounting_types
    )
    
    print("\n=== Test: Montagetyp-Validierung ===")
    
    # Test 1: Satteldach mit Aufdach-Montage sollte VALID sein
    print("\n📋 Test 1: Satteldach + Aufdach-Montage")
    allowed = get_allowed_mounting_types("Satteldach")
    print(f"  Erlaubte Typen für Satteldach: {allowed}")
    
    validation = validate_mounting_selection("Satteldach", "Aufdach-Montage")
    print(f"  Validierung: {validation}")
    
    assert validation["valid"] == True, \
        "Aufdach-Montage sollte für Satteldach VALID sein"
    assert validation["error"] is None, \
        "Es sollte KEINE Fehlermeldung geben"
    print("  ✓ Aufdach-Montage ist für Satteldach VALID")
    
    # Test 2: Satteldach mit Aufständerung sollte INVALID sein
    print("\n📋 Test 2: Satteldach + Aufständerung Süd")
    validation = validate_mounting_selection("Satteldach", "Aufständerung Süd")
    print(f"  Validierung: {validation}")
    
    assert validation["valid"] == False, \
        "Aufständerung sollte für Satteldach INVALID sein"
    assert "Aufständerungen sind nur für Flachdächer erlaubt" in validation["error"], \
        "Fehlermeldung sollte klar sein"
    print("  ✓ Aufständerung wird für Satteldach korrekt abgelehnt")
    
    # Test 3: Flachdach mit Aufständerung sollte VALID sein
    print("\n📋 Test 3: Flachdach + Aufständerung Süd")
    allowed = get_allowed_mounting_types("Flachdach")
    print(f"  Erlaubte Typen für Flachdach: {allowed}")
    
    validation = validate_mounting_selection("Flachdach", "Aufständerung Süd")
    print(f"  Validierung: {validation}")
    
    assert validation["valid"] == True, \
        "Aufständerung sollte für Flachdach VALID sein"
    assert validation["error"] is None, \
        "Es sollte KEINE Fehlermeldung geben"
    print("  ✓ Aufständerung ist für Flachdach VALID")
    
    # Test 4: Flachdach mit Aufdach-Montage sollte VALID sein (aber nicht optimal)
    print("\n📋 Test 4: Flachdach + Aufdach-Montage")
    validation = validate_mounting_selection("Flachdach", "Aufdach-Montage")
    print(f"  Validierung: {validation}")
    
    # Aufdach-Montage ist nicht in den erlaubten Typen für Flachdach
    # Also sollte es eine Warnung geben
    if "Aufdach-Montage" not in allowed:
        assert validation["valid"] == False, \
            "Aufdach-Montage sollte für Flachdach nicht optimal sein"
        print("  ✓ Aufdach-Montage wird für Flachdach als nicht optimal markiert")
    else:
        print("  ℹ️ Aufdach-Montage ist für Flachdach erlaubt")
    
    print("\n✅ Alle Tests bestanden!")


if __name__ == "__main__":
    print("=" * 70)
    print("MONTAGETYP-VALIDIERUNG FIX - TEST SUITE")
    print("=" * 70)
    
    try:
        test_mounting_validation()
        
        print("\n" + "=" * 70)
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
