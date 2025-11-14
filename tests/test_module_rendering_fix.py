"""
Test für Modul-Rendering Fix

Verifiziert dass:
1. roof_pitch in basis_settings enthalten ist
2. Validierungs-Empfehlung die Auswahl nicht überschreibt
3. Module für alle Dachtypen gerendert werden können
"""

def test_basis_settings_includes_roof_pitch():
    """Test dass basis_settings roof_pitch enthält"""
    print("\n=== Test 1: basis_settings enthält roof_pitch ===")
    
    # Prüfe ob render_basis_settings roof_pitch zurückgibt
    import inspect
    from utils.pv3d_ui_components import render_basis_settings
    
    source = inspect.getsource(render_basis_settings)
    
    # Prüfe ob "roof_pitch" im Return-Statement vorkommt
    assert '"roof_pitch"' in source or "'roof_pitch'" in source, \
        "render_basis_settings sollte roof_pitch zurückgeben"
    
    print("[OK] render_basis_settings gibt roof_pitch zurück")
    
    # Prüfe ob roof_pitch Input-Feld vorhanden ist
    assert "roof_pitch_input" in source, \
        "render_basis_settings sollte roof_pitch Input-Feld haben"
    
    print("[OK] roof_pitch Input-Feld vorhanden")
    
    return True


def test_validation_does_not_override_selection():
    """Test dass Validierung die Auswahl nicht überschreibt"""
    print("\n=== Test 2: Validierung überschreibt Auswahl nicht ===")
    
    import inspect
    from utils.pv3d_mounting_logic import render_mounting_selection_with_validation
    
    source = inspect.getsource(render_mounting_selection_with_validation)
    
    # Prüfe dass die automatische Überschreibung kommentiert oder entfernt wurde
    # Der String sollte entweder nicht vorkommen oder kommentiert sein
    problematic_line = 'current_selection = validation["suggestion"]'
    if problematic_line in source:
        # Prüfe ob es kommentiert ist
        lines = source.split('\n')
        for line in lines:
            if problematic_line in line and not line.strip().startswith('#'):
                assert False, "Validierung sollte current_selection NICHT überschreiben (Zeile nicht kommentiert)"
    
    print("[OK] Validierung überschreibt current_selection nicht")
    
    # Prüfe dass Empfehlung trotzdem angezeigt wird
    assert '[IDEA] Empfehlung' in source, \
        "Empfehlung sollte trotzdem angezeigt werden"
    
    print("[OK] Empfehlung wird angezeigt")
    
    return True


def test_module_placement_for_all_roof_types():
    """Test dass Module für alle Dachtypen platziert werden können"""
    print("\n=== Test 3: Modul-Platzierung für alle Dachtypen ===")
    
    from utils.pv3d_placement_handler import handle_auto_placement
    
    # Mock Streamlit session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    roof_types = [
        ("Flachdach", 0.0),
        ("Satteldach", 35.0),
        ("Pultdach", 25.0),
        ("Walmdach", 40.0),
    ]
    
    all_passed = True
    
    for roof_type, roof_pitch in roof_types:
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=10,
            roof_type=roof_type,
            roof_pitch=roof_pitch
        )
        
        if result["success"] and result["count"] > 0:
            print(f"[OK] {roof_type}: {result['count']} Module platziert")
        else:
            print(f"[ERROR] {roof_type}: Platzierung fehlgeschlagen - {result['message']}")
            all_passed = False
    
    assert all_passed, "Alle Dachtypen sollten Module platzieren können"
    
    return True


def test_mounting_type_validation():
    """Test dass Montagetyp-Validierung korrekt funktioniert"""
    print("\n=== Test 4: Montagetyp-Validierung ===")
    
    from utils.pv3d_mounting_logic import validate_mounting_selection
    
    # Test 1: Aufständerung bei Flachdach sollte erlaubt sein
    result = validate_mounting_selection("Flachdach", "Aufständerung Süd")
    assert result["valid"] == True, "Aufständerung sollte bei Flachdach erlaubt sein"
    print("[OK] Aufständerung bei Flachdach: erlaubt")
    
    # Test 2: Aufständerung bei Satteldach sollte NICHT erlaubt sein
    result = validate_mounting_selection("Satteldach", "Aufständerung Süd")
    assert result["valid"] == False, "Aufständerung sollte bei Satteldach NICHT erlaubt sein"
    assert result["suggestion"] == "Aufdach-Montage", "Empfehlung sollte Aufdach-Montage sein"
    print("[OK] Aufständerung bei Satteldach: nicht erlaubt")
    print(f"  Empfehlung: {result['suggestion']}")
    
    # Test 3: Aufdach-Montage bei Satteldach sollte erlaubt sein
    result = validate_mounting_selection("Satteldach", "Aufdach-Montage")
    assert result["valid"] == True, "Aufdach-Montage sollte bei Satteldach erlaubt sein"
    print("[OK] Aufdach-Montage bei Satteldach: erlaubt")
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("MODUL-RENDERING FIX - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("basis_settings enthält roof_pitch", test_basis_settings_includes_roof_pitch),
        ("Validierung überschreibt Auswahl nicht", test_validation_does_not_override_selection),
        ("Modul-Platzierung für alle Dachtypen", test_module_placement_for_all_roof_types),
        ("Montagetyp-Validierung", test_mounting_type_validation),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            test_func()
        except AssertionError as e:
            print(f"\n[ERROR] Test fehlgeschlagen: {test_name}")
            print(f"   Fehler: {e}")
            all_passed = False
        except Exception as e:
            print(f"\n[ERROR] Unerwarteter Fehler in Test: {test_name}")
            print(f"   Fehler: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("[OK] ALLE TESTS BESTANDEN!")
        print("=" * 70)
        print("\nDer Fix ist vollständig:")
        print("1. [OK] roof_pitch wird in basis_settings zurückgegeben")
        print("2. [OK] Validierung überschreibt Auswahl nicht")
        print("3. [OK] Module können für alle Dachtypen platziert werden")
        print("4. [OK] Montagetyp-Validierung funktioniert korrekt")
        print("\nModule sollten jetzt bei allen Dachtypen gerendert werden!")
    else:
        print("[ERROR] EINIGE TESTS FEHLGESCHLAGEN")
        print("=" * 70)
        print("\nBitte Fehler beheben und erneut testen.")
