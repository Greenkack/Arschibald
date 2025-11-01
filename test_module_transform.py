"""
Test für ModuleTransform Datenklasse (Task 11.1)
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import ModuleTransform


def test_module_transform_creation():
    """Test: Erstelle ModuleTransform mit Standardwerten"""
    print("Test 1: ModuleTransform mit Standardwerten...")
    
    transform = ModuleTransform(index=0)
    
    assert transform.index == 0
    assert transform.azimuth_deg == 0.0
    assert transform.tilt_deg == 15.0
    assert transform.offset_x == 0.0
    assert transform.offset_y == 0.0
    assert transform.offset_z == 0.0
    assert transform.group_id is None
    
    print("✓ ModuleTransform mit Standardwerten erfolgreich erstellt")


def test_module_transform_custom_values():
    """Test: Erstelle ModuleTransform mit benutzerdefinierten Werten"""
    print("\nTest 2: ModuleTransform mit benutzerdefinierten Werten...")
    
    transform = ModuleTransform(
        index=5,
        azimuth_deg=180.0,
        tilt_deg=30.0,
        offset_x=1.5,
        offset_y=-0.5,
        offset_z=0.2,
        group_id="south_roof"
    )
    
    assert transform.index == 5
    assert transform.azimuth_deg == 180.0
    assert transform.tilt_deg == 30.0
    assert transform.offset_x == 1.5
    assert transform.offset_y == -0.5
    assert transform.offset_z == 0.2
    assert transform.group_id == "south_roof"
    
    print("✓ ModuleTransform mit benutzerdefinierten Werten erfolgreich erstellt")


def test_azimuth_validation():
    """Test: Validierung von Azimuth-Werten (0-360°)"""
    print("\nTest 3: Azimuth-Validierung...")
    
    # Gültige Werte
    transform1 = ModuleTransform(index=0, azimuth_deg=0.0)
    assert transform1.azimuth_deg == 0.0
    
    transform2 = ModuleTransform(index=1, azimuth_deg=180.0)
    assert transform2.azimuth_deg == 180.0
    
    transform3 = ModuleTransform(index=2, azimuth_deg=360.0)
    assert transform3.azimuth_deg == 360.0
    
    # Ungültige Werte
    try:
        ModuleTransform(index=3, azimuth_deg=-10.0)
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        assert "Azimuth" in str(e)
        print(f"  ✓ Ungültiger Azimuth -10° korrekt abgelehnt: {e}")
    
    try:
        ModuleTransform(index=4, azimuth_deg=370.0)
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        assert "Azimuth" in str(e)
        print(f"  ✓ Ungültiger Azimuth 370° korrekt abgelehnt: {e}")
    
    print("✓ Azimuth-Validierung funktioniert korrekt")


def test_tilt_validation():
    """Test: Validierung von Neigungs-Werten (0-90°)"""
    print("\nTest 4: Neigungs-Validierung...")
    
    # Gültige Werte
    transform1 = ModuleTransform(index=0, tilt_deg=0.0)
    assert transform1.tilt_deg == 0.0
    
    transform2 = ModuleTransform(index=1, tilt_deg=45.0)
    assert transform2.tilt_deg == 45.0
    
    transform3 = ModuleTransform(index=2, tilt_deg=90.0)
    assert transform3.tilt_deg == 90.0
    
    # Ungültige Werte
    try:
        ModuleTransform(index=3, tilt_deg=-5.0)
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        assert "Neigung" in str(e)
        print(f"  ✓ Ungültige Neigung -5° korrekt abgelehnt: {e}")
    
    try:
        ModuleTransform(index=4, tilt_deg=95.0)
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        assert "Neigung" in str(e)
        print(f"  ✓ Ungültige Neigung 95° korrekt abgelehnt: {e}")
    
    print("✓ Neigungs-Validierung funktioniert korrekt")


def test_to_dict():
    """Test: Konvertierung zu Dictionary"""
    print("\nTest 5: to_dict() Methode...")
    
    transform = ModuleTransform(
        index=10,
        azimuth_deg=90.0,
        tilt_deg=25.0,
        offset_x=0.5,
        offset_y=1.0,
        offset_z=-0.3,
        group_id="west_roof"
    )
    
    data = transform.to_dict()
    
    assert data["index"] == 10
    assert data["azimuth_deg"] == 90.0
    assert data["tilt_deg"] == 25.0
    assert data["offset_x"] == 0.5
    assert data["offset_y"] == 1.0
    assert data["offset_z"] == -0.3
    assert data["group_id"] == "west_roof"
    
    print(f"  Dictionary: {data}")
    print("✓ to_dict() funktioniert korrekt")


def test_from_dict():
    """Test: Erstellung aus Dictionary"""
    print("\nTest 6: from_dict() Methode...")
    
    data = {
        "index": 15,
        "azimuth_deg": 270.0,
        "tilt_deg": 35.0,
        "offset_x": -1.0,
        "offset_y": 0.5,
        "offset_z": 0.1,
        "group_id": "east_roof"
    }
    
    transform = ModuleTransform.from_dict(data)
    
    assert transform.index == 15
    assert transform.azimuth_deg == 270.0
    assert transform.tilt_deg == 35.0
    assert transform.offset_x == -1.0
    assert transform.offset_y == 0.5
    assert transform.offset_z == 0.1
    assert transform.group_id == "east_roof"
    
    print("✓ from_dict() funktioniert korrekt")


def test_from_dict_with_defaults():
    """Test: from_dict() mit fehlenden optionalen Feldern"""
    print("\nTest 7: from_dict() mit Standardwerten...")
    
    # Minimales Dictionary (nur index erforderlich)
    data = {"index": 20}
    
    transform = ModuleTransform.from_dict(data)
    
    assert transform.index == 20
    assert transform.azimuth_deg == 0.0  # Standardwert
    assert transform.tilt_deg == 15.0    # Standardwert
    assert transform.offset_x == 0.0     # Standardwert
    assert transform.offset_y == 0.0     # Standardwert
    assert transform.offset_z == 0.0     # Standardwert
    assert transform.group_id is None    # Standardwert
    
    print("✓ from_dict() mit Standardwerten funktioniert korrekt")


def test_from_dict_invalid():
    """Test: from_dict() mit ungültigen Daten"""
    print("\nTest 8: from_dict() mit ungültigen Daten...")
    
    # Fehlendes index-Feld
    try:
        ModuleTransform.from_dict({"azimuth_deg": 45.0})
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        print(f"  ✓ Fehlendes index-Feld korrekt abgelehnt: {e}")
    
    # Ungültiger Azimuth
    try:
        ModuleTransform.from_dict({"index": 0, "azimuth_deg": 400.0})
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        print(f"  ✓ Ungültiger Azimuth korrekt abgelehnt: {e}")
    
    print("✓ from_dict() Fehlerbehandlung funktioniert korrekt")


def test_roundtrip():
    """Test: Roundtrip to_dict() -> from_dict()"""
    print("\nTest 9: Roundtrip to_dict() -> from_dict()...")
    
    original = ModuleTransform(
        index=42,
        azimuth_deg=135.0,
        tilt_deg=20.0,
        offset_x=2.5,
        offset_y=-1.5,
        offset_z=0.8,
        group_id="test_group"
    )
    
    # Konvertiere zu Dictionary und zurück
    data = original.to_dict()
    restored = ModuleTransform.from_dict(data)
    
    # Vergleiche alle Felder
    assert restored.index == original.index
    assert restored.azimuth_deg == original.azimuth_deg
    assert restored.tilt_deg == original.tilt_deg
    assert restored.offset_x == original.offset_x
    assert restored.offset_y == original.offset_y
    assert restored.offset_z == original.offset_z
    assert restored.group_id == original.group_id
    
    print("✓ Roundtrip funktioniert korrekt")


def main():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("ModuleTransform Tests (Task 11.1)")
    print("=" * 70)
    
    try:
        test_module_transform_creation()
        test_module_transform_custom_values()
        test_azimuth_validation()
        test_tilt_validation()
        test_to_dict()
        test_from_dict()
        test_from_dict_with_defaults()
        test_from_dict_invalid()
        test_roundtrip()
        
        print("\n" + "=" * 70)
        print("✓ ALLE TESTS ERFOLGREICH")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ UNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
