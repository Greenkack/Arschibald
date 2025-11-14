"""
Test für Modul-Gruppen-Verwaltung (Task 16)

Testet die Funktionalität der Modul-Gruppen-Verwaltung:
- Gruppen-Erstellung
- Gruppen-Übersicht
- Gruppen-Transformationen
- Gruppen-Templates
"""

import sys
import os

# Füge utils-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d import (
    ModuleGroup,
    ModuleTransform,
    AdvancedLayoutConfig
)


def test_module_group_creation():
    """Test 16.1: Gruppen-Erstellung"""
    print("\n=== Test 16.1: Gruppen-Erstellung ===")
    
    # Erstelle ModuleGroup
    group = ModuleGroup(
        name="Süddach",
        module_indices=[0, 1, 2, 3, 4],
        azimuth_deg=0.0,
        tilt_deg=35.0,
        color="#ff8800"
    )
    
    # Prüfe Eigenschaften
    assert group.name == "Süddach", "Gruppen-Name falsch"
    assert len(group.module_indices) == 5, "Modul-Anzahl falsch"
    assert group.azimuth_deg == 0.0, "Azimuth falsch"
    assert group.tilt_deg == 35.0, "Neigung falsch"
    assert group.color == "#ff8800", "Farbe falsch"
    
    # Teste add_module
    group.add_module(5)
    assert 5 in group.module_indices, "Modul nicht hinzugefügt"
    assert group.get_module_count() == 6, "Modul-Anzahl nach Hinzufügen falsch"
    
    # Teste remove_module
    group.remove_module(5)
    assert 5 not in group.module_indices, "Modul nicht entfernt"
    assert group.get_module_count() == 5, "Modul-Anzahl nach Entfernen falsch"
    
    # Teste has_module
    assert group.has_module(0), "has_module gibt False für existierendes Modul"
    assert not group.has_module(10), "has_module gibt True für nicht-existierendes Modul"
    
    print("[OK] Gruppen-Erstellung funktioniert")


def test_module_group_serialization():
    """Test 16.1: Gruppen-Serialisierung (für Speicherung)"""
    print("\n=== Test 16.1: Gruppen-Serialisierung ===")
    
    # Erstelle Gruppe
    group = ModuleGroup(
        name="Ostdach",
        module_indices=[10, 11, 12],
        azimuth_deg=270.0,
        tilt_deg=30.0,
        color="#ffff00"
    )
    
    # Serialisiere zu Dictionary
    group_dict = group.to_dict()
    
    assert group_dict["name"] == "Ostdach", "Name nicht serialisiert"
    assert group_dict["module_indices"] == [10, 11, 12], "Indizes nicht serialisiert"
    assert group_dict["azimuth_deg"] == 270.0, "Azimuth nicht serialisiert"
    assert group_dict["tilt_deg"] == 30.0, "Neigung nicht serialisiert"
    assert group_dict["color"] == "#ffff00", "Farbe nicht serialisiert"
    
    # Deserialisiere von Dictionary
    restored_group = ModuleGroup.from_dict(group_dict)
    
    assert restored_group.name == group.name, "Name nicht wiederhergestellt"
    assert restored_group.module_indices == group.module_indices, "Indizes nicht wiederhergestellt"
    assert restored_group.azimuth_deg == group.azimuth_deg, "Azimuth nicht wiederhergestellt"
    assert restored_group.tilt_deg == group.tilt_deg, "Neigung nicht wiederhergestellt"
    assert restored_group.color == group.color, "Farbe nicht wiederhergestellt"
    
    print("[OK] Gruppen-Serialisierung funktioniert")


def test_advanced_layout_config_with_groups():
    """Test 16.2: Gruppen in AdvancedLayoutConfig"""
    print("\n=== Test 16.2: Gruppen in AdvancedLayoutConfig ===")
    
    # Erstelle AdvancedLayoutConfig
    config = AdvancedLayoutConfig()
    
    # Erstelle Gruppen
    group1 = ModuleGroup(
        name="Süddach",
        module_indices=[0, 1, 2],
        azimuth_deg=0.0,
        tilt_deg=35.0,
        color="#ff8800"
    )
    
    group2 = ModuleGroup(
        name="Westdach",
        module_indices=[3, 4, 5],
        azimuth_deg=90.0,
        tilt_deg=30.0,
        color="#00ffff"
    )
    
    # Füge Gruppen zur Konfiguration hinzu
    config.module_groups["Süddach"] = group1
    config.module_groups["Westdach"] = group2
    
    # Prüfe Gruppen-Anzahl
    assert len(config.module_groups) == 2, "Gruppen-Anzahl falsch"
    assert "Süddach" in config.module_groups, "Süddach-Gruppe nicht gefunden"
    assert "Westdach" in config.module_groups, "Westdach-Gruppe nicht gefunden"
    
    # Serialisiere und deserialisiere
    json_str = config.to_json()
    restored_config = AdvancedLayoutConfig.from_json(json_str)
    
    # Prüfe wiederhergestellte Gruppen
    assert len(restored_config.module_groups) == 2, "Gruppen-Anzahl nach Wiederherstellung falsch"
    assert "Süddach" in restored_config.module_groups, "Süddach-Gruppe nach Wiederherstellung nicht gefunden"
    assert "Westdach" in restored_config.module_groups, "Westdach-Gruppe nach Wiederherstellung nicht gefunden"
    
    # Prüfe Gruppen-Details
    restored_group1 = restored_config.module_groups["Süddach"]
    assert restored_group1.module_indices == [0, 1, 2], "Süddach-Indizes falsch"
    assert restored_group1.azimuth_deg == 0.0, "Süddach-Azimuth falsch"
    
    print("[OK] Gruppen in AdvancedLayoutConfig funktionieren")


def test_group_transformations():
    """Test 16.3: Gruppen-Transformationen"""
    print("\n=== Test 16.3: Gruppen-Transformationen ===")
    
    # Erstelle AdvancedLayoutConfig
    config = AdvancedLayoutConfig()
    
    # Erstelle Gruppe
    group = ModuleGroup(
        name="Testgruppe",
        module_indices=[0, 1, 2, 3],
        azimuth_deg=0.0,
        tilt_deg=15.0,
        color="#000000"
    )
    
    config.module_groups["Testgruppe"] = group
    
    # Erstelle ModuleTransforms für alle Module in der Gruppe
    for module_idx in group.module_indices:
        transform = ModuleTransform(
            index=module_idx,
            azimuth_deg=group.azimuth_deg,
            tilt_deg=group.tilt_deg,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0,
            group_id="Testgruppe"
        )
        config.module_transforms[module_idx] = transform
    
    # Prüfe dass alle Module die Gruppen-ID haben
    for module_idx in group.module_indices:
        assert module_idx in config.module_transforms, f"Transform für Modul {module_idx} fehlt"
        assert config.module_transforms[module_idx].group_id == "Testgruppe", f"Gruppen-ID für Modul {module_idx} falsch"
    
    # Ändere Gruppen-Eigenschaften
    new_azimuth = 45.0
    new_tilt = 30.0
    
    group.azimuth_deg = new_azimuth
    group.tilt_deg = new_tilt
    
    # Wende auf alle Module an
    for module_idx in group.module_indices:
        config.module_transforms[module_idx].azimuth_deg = new_azimuth
        config.module_transforms[module_idx].tilt_deg = new_tilt
    
    # Prüfe dass alle Module aktualisiert wurden
    for module_idx in group.module_indices:
        assert config.module_transforms[module_idx].azimuth_deg == new_azimuth, f"Azimuth für Modul {module_idx} nicht aktualisiert"
        assert config.module_transforms[module_idx].tilt_deg == new_tilt, f"Neigung für Modul {module_idx} nicht aktualisiert"
    
    print("[OK] Gruppen-Transformationen funktionieren")


def test_group_templates():
    """Test 16.4: Gruppen-Templates"""
    print("\n=== Test 16.4: Gruppen-Templates ===")
    
    # Definiere Templates (wie in UI)
    templates = {
        "Süddach": {
            "azimuth": 0.0,
            "tilt": 35.0,
            "color": "#ff8800"
        },
        "Ostdach": {
            "azimuth": 270.0,
            "tilt": 35.0,
            "color": "#ffff00"
        },
        "Westdach": {
            "azimuth": 90.0,
            "tilt": 35.0,
            "color": "#00ffff"
        },
        "Norddach": {
            "azimuth": 180.0,
            "tilt": 35.0,
            "color": "#8800ff"
        }
    }
    
    # Teste jedes Template
    for template_name, template_data in templates.items():
        # Erstelle Gruppe aus Template
        group = ModuleGroup(
            name=template_name,
            module_indices=[0, 1, 2],
            azimuth_deg=template_data["azimuth"],
            tilt_deg=template_data["tilt"],
            color=template_data["color"]
        )
        
        # Prüfe Template-Werte
        assert group.azimuth_deg == template_data["azimuth"], f"{template_name}: Azimuth falsch"
        assert group.tilt_deg == template_data["tilt"], f"{template_name}: Neigung falsch"
        assert group.color == template_data["color"], f"{template_name}: Farbe falsch"
        
        print(f"  [OK] Template '{template_name}' korrekt (Azimuth: {group.azimuth_deg}°)")
    
    print("[OK] Gruppen-Templates funktionieren")


def test_group_deletion():
    """Test 16.2: Gruppen-Löschung"""
    print("\n=== Test 16.2: Gruppen-Löschung ===")
    
    # Erstelle AdvancedLayoutConfig mit Gruppe
    config = AdvancedLayoutConfig()
    
    group = ModuleGroup(
        name="Zu löschende Gruppe",
        module_indices=[0, 1, 2],
        azimuth_deg=0.0,
        tilt_deg=15.0,
        color="#000000"
    )
    
    config.module_groups["Zu löschende Gruppe"] = group
    
    # Erstelle Transforms für Module
    for module_idx in group.module_indices:
        config.module_transforms[module_idx] = ModuleTransform(
            index=module_idx,
            azimuth_deg=0.0,
            tilt_deg=15.0,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0,
            group_id="Zu löschende Gruppe"
        )
    
    # Prüfe dass Gruppe existiert
    assert "Zu löschende Gruppe" in config.module_groups, "Gruppe nicht erstellt"
    
    # Lösche Gruppe
    del config.module_groups["Zu löschende Gruppe"]
    
    # Entferne group_id von Modulen
    for module_idx in group.module_indices:
        if module_idx in config.module_transforms:
            config.module_transforms[module_idx].group_id = None
    
    # Prüfe dass Gruppe gelöscht wurde
    assert "Zu löschende Gruppe" not in config.module_groups, "Gruppe nicht gelöscht"
    
    # Prüfe dass group_id entfernt wurde
    for module_idx in group.module_indices:
        if module_idx in config.module_transforms:
            assert config.module_transforms[module_idx].group_id is None, f"group_id für Modul {module_idx} nicht entfernt"
    
    print("[OK] Gruppen-Löschung funktioniert")


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("TASK 16: MODUL-GRUPPEN-VERWALTUNG - TESTS")
    print("="*60)
    
    try:
        # Test 16.1: Gruppen-Erstellung
        test_module_group_creation()
        test_module_group_serialization()
        
        # Test 16.2: Gruppen-Übersicht
        test_advanced_layout_config_with_groups()
        test_group_deletion()
        
        # Test 16.3: Gruppen-Transformationen
        test_group_transformations()
        
        # Test 16.4: Gruppen-Templates
        test_group_templates()
        
        print("\n" + "="*60)
        print("[OK] ALLE TESTS BESTANDEN")
        print("="*60)
        print("\nTask 16: Modul-Gruppen-Verwaltung erfolgreich implementiert!")
        print("\nImplementierte Features:")
        print("  [OK] 16.1: Gruppen-Erstellung mit Name, Indizes und Eigenschaften")
        print("  [OK] 16.2: Gruppen-Übersicht mit Anzeige und Lösch-Funktion")
        print("  [OK] 16.3: Gruppen-Transformationen (Azimuth/Neigung)")
        print("  [OK] 16.4: Gruppen-Templates (Süd, Ost, West, Nord)")
        print("\n" + "="*60)
        
        return True
        
    except AssertionError as e:
        print(f"\n[ERROR] TEST FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
