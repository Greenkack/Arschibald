"""
Test für ModuleGroup Datenklasse (Task 11.2)
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import ModuleGroup


def test_module_group_creation():
    """Test: Erstelle ModuleGroup mit Standardwerten"""
    print("Test 1: ModuleGroup mit Standardwerten...")
    
    group = ModuleGroup(name="test_group")
    
    assert group.name == "test_group"
    assert group.module_indices == []
    assert group.azimuth_deg == 0.0
    assert group.tilt_deg == 15.0
    assert group.color == "#000000"
    
    print("ModuleGroup mit Standardwerten erfolgreich erstellt")


def test_module_group_custom_values():
    """Test: Erstelle ModuleGroup mit benutzerdefinierten Werten"""
    print("\nTest 2: ModuleGroup mit benutzerdefinierten Werten...")
    
    group = ModuleGroup(
        name="south_roof",
        module_indices=[0, 1, 2, 3, 4],
        azimuth_deg=180.0,
        tilt_deg=30.0,
        color="#ff0000"
    )
    
    assert group.name == "south_roof"
    assert group.module_indices == [0, 1, 2, 3, 4]
    assert group.azimuth_deg == 180.0
    assert group.tilt_deg == 30.0
    assert group.color == "#ff0000"
    
    print("ModuleGroup mit benutzerdefinierten Werten erfolgreich erstellt")


def test_add_module():
    """Test: Module zur Gruppe hinzufügen"""
    print("\nTest 3: add_module() Methode...")
    
    group = ModuleGroup(name="test_group")
    
    # Füge Module hinzu
    group.add_module(0)
    assert group.module_indices == [0]
    
    group.add_module(5)
    assert group.module_indices == [0, 5]
    
    group.add_module(10)
    assert group.module_indices == [0, 5, 10]
    
    print(f"  Module in Gruppe: {group.module_indices}")
    
    # Versuche doppeltes Modul hinzuzufügen
    try:
        group.add_module(5)
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        assert "bereits in Gruppe" in str(e)
        print(f"  Doppeltes Modul korrekt abgelehnt: {e}")
    
    print("add_module() funktioniert korrekt")


def test_remove_module():
    """Test: Module aus Gruppe entfernen"""
    print("\nTest 4: remove_module() Methode...")
    
    group = ModuleGroup(
        name="test_group",
        module_indices=[0, 5, 10, 15]
    )
    
    # Entferne Module
    group.remove_module(5)
    assert group.module_indices == [0, 10, 15]
    
    group.remove_module(0)
    assert group.module_indices == [10, 15]
    
    print(f"  Verbleibende Module: {group.module_indices}")
    
    # Versuche nicht-existierendes Modul zu entfernen
    try:
        group.remove_module(99)
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        assert "nicht in Gruppe" in str(e)
        print(f"  Nicht-existierendes Modul korrekt abgelehnt: {e}")
    
    print("remove_module() funktioniert korrekt")


def test_has_module():
    """Test: Prüfe ob Modul in Gruppe ist"""
    print("\nTest 5: has_module() Methode...")
    
    group = ModuleGroup(
        name="test_group",
        module_indices=[1, 3, 5, 7, 9]
    )
    
    # Prüfe existierende Module
    assert group.has_module(1) is True
    assert group.has_module(5) is True
    assert group.has_module(9) is True
    
    # Prüfe nicht-existierende Module
    assert group.has_module(0) is False
    assert group.has_module(2) is False
    assert group.has_module(10) is False
    
    print("has_module() funktioniert korrekt")


def test_get_module_count():
    """Test: Anzahl der Module in Gruppe"""
    print("\nTest 6: get_module_count() Methode...")
    
    group1 = ModuleGroup(name="empty_group")
    assert group1.get_module_count() == 0
    
    group2 = ModuleGroup(
        name="small_group",
        module_indices=[0, 1, 2]
    )
    assert group2.get_module_count() == 3
    
    group3 = ModuleGroup(
        name="large_group",
        module_indices=list(range(20))
    )
    assert group3.get_module_count() == 20
    
    print("get_module_count() funktioniert korrekt")


def test_to_dict():
    """Test: Konvertierung zu Dictionary"""
    print("\nTest 7: to_dict() Methode...")
    
    group = ModuleGroup(
        name="west_roof",
        module_indices=[10, 11, 12, 13],
        azimuth_deg=90.0,
        tilt_deg=25.0,
        color="#00ff00"
    )
    
    data = group.to_dict()
    
    assert data["name"] == "west_roof"
    assert data["module_indices"] == [10, 11, 12, 13]
    assert data["azimuth_deg"] == 90.0
    assert data["tilt_deg"] == 25.0
    assert data["color"] == "#00ff00"
    
    # Prüfe dass Liste kopiert wurde (nicht Referenz)
    data["module_indices"].append(999)
    assert 999 not in group.module_indices
    
    print(f"  Dictionary: {data}")
    print("to_dict() funktioniert korrekt")


def test_from_dict():
    """Test: Erstellung aus Dictionary"""
    print("\nTest 8: from_dict() Methode...")
    
    data = {
        "name": "east_roof",
        "module_indices": [20, 21, 22, 23, 24],
        "azimuth_deg": 270.0,
        "tilt_deg": 35.0,
        "color": "#0000ff"
    }
    
    group = ModuleGroup.from_dict(data)
    
    assert group.name == "east_roof"
    assert group.module_indices == [20, 21, 22, 23, 24]
    assert group.azimuth_deg == 270.0
    assert group.tilt_deg == 35.0
    assert group.color == "#0000ff"
    
    print("from_dict() funktioniert korrekt")


def test_from_dict_with_defaults():
    """Test: from_dict() mit fehlenden optionalen Feldern"""
    print("\nTest 9: from_dict() mit Standardwerten...")
    
    # Minimales Dictionary (nur name erforderlich)
    data = {"name": "minimal_group"}
    
    group = ModuleGroup.from_dict(data)
    
    assert group.name == "minimal_group"
    assert group.module_indices == []      # Standardwert
    assert group.azimuth_deg == 0.0        # Standardwert
    assert group.tilt_deg == 15.0          # Standardwert
    assert group.color == "#000000"        # Standardwert
    
    print("from_dict() mit Standardwerten funktioniert korrekt")


def test_from_dict_invalid():
    """Test: from_dict() mit ungültigen Daten"""
    print("\nTest 10: from_dict() mit ungültigen Daten...")
    
    # Fehlendes name-Feld
    try:
        ModuleGroup.from_dict({"azimuth_deg": 45.0})
        assert False, "Sollte ValueError werfen"
    except ValueError as e:
        print(f"  Fehlendes name-Feld korrekt abgelehnt: {e}")
    
    print("from_dict() Fehlerbehandlung funktioniert korrekt")


def test_roundtrip():
    """Test: Roundtrip to_dict() -> from_dict()"""
    print("\nTest 11: Roundtrip to_dict() -> from_dict()...")
    
    original = ModuleGroup(
        name="test_roundtrip",
        module_indices=[5, 10, 15, 20, 25],
        azimuth_deg=135.0,
        tilt_deg=20.0,
        color="#ff00ff"
    )
    
    # Konvertiere zu Dictionary und zurück
    data = original.to_dict()
    restored = ModuleGroup.from_dict(data)
    
    # Vergleiche alle Felder
    assert restored.name == original.name
    assert restored.module_indices == original.module_indices
    assert restored.azimuth_deg == original.azimuth_deg
    assert restored.tilt_deg == original.tilt_deg
    assert restored.color == original.color
    
    print("Roundtrip funktioniert korrekt")


def test_module_operations_workflow():
    """Test: Kompletter Workflow mit Modul-Operationen"""
    print("\nTest 12: Kompletter Workflow...")
    
    # Erstelle Gruppe
    group = ModuleGroup(name="workflow_test")
    assert group.get_module_count() == 0
    
    # Füge Module hinzu
    for i in range(5):
        group.add_module(i)
    assert group.get_module_count() == 5
    
    # Prüfe Module
    assert group.has_module(2) is True
    assert group.has_module(10) is False
    
    # Entferne einige Module
    group.remove_module(1)
    group.remove_module(3)
    assert group.get_module_count() == 3
    assert group.module_indices == [0, 2, 4]
    
    # Füge weitere Module hinzu
    group.add_module(10)
    group.add_module(20)
    assert group.get_module_count() == 5
    assert group.module_indices == [0, 2, 4, 10, 20]
    
    print(f"  Finale Module: {group.module_indices}")
    print("Kompletter Workflow funktioniert korrekt")


def main():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("ModuleGroup Tests (Task 11.2)")
    print("=" * 70)
    
    try:
        test_module_group_creation()
        test_module_group_custom_values()
        test_add_module()
        test_remove_module()
        test_has_module()
        test_get_module_count()
        test_to_dict()
        test_from_dict()
        test_from_dict_with_defaults()
        test_from_dict_invalid()
        test_roundtrip()
        test_module_operations_workflow()
        
        print("\n" + "=" * 70)
        print("ALLE TESTS ERFOLGREICH")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\nTEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\nUNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
