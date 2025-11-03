"""
Test für AdvancedLayoutConfig Datenklasse (Task 11.3)
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import AdvancedLayoutConfig, ModuleTransform, ModuleGroup


def test_advanced_layout_config_creation():
    """Test: Erstelle AdvancedLayoutConfig mit Standardwerten"""
    print("Test 1: AdvancedLayoutConfig mit Standardwerten...")
    
    config = AdvancedLayoutConfig()
    
    # Basis-Felder von LayoutConfig
    assert config.mode == "auto"
    assert config.use_garage is False
    assert config.use_facade is False
    assert config.removed_indices == []
    assert config.garage_dims == (6.0, 3.0, 3.0)
    assert config.offset_main_xy == (0.0, 0.0)
    assert config.offset_garage_xy == (0.0, 0.0)
    
    # Erweiterte Felder
    assert config.module_transforms == {}
    assert config.module_groups == {}
    assert config.mounting_mode == "south"
    assert config.custom_azimuth == 0.0
    assert config.custom_tilt == 15.0
    assert config.enable_collision_detection is True
    assert config.enable_shading_analysis is False
    
    print("✓ AdvancedLayoutConfig mit Standardwerten erfolgreich erstellt")


def test_advanced_layout_config_with_transforms():
    """Test: AdvancedLayoutConfig mit ModuleTransforms"""
    print("\nTest 2: AdvancedLayoutConfig mit ModuleTransforms...")
    
    # Erstelle einige Transformationen
    transform1 = ModuleTransform(index=0, azimuth_deg=90.0, tilt_deg=20.0)
    transform2 = ModuleTransform(index=5, azimuth_deg=180.0, tilt_deg=25.0)
    transform3 = ModuleTransform(index=10, azimuth_deg=270.0, tilt_deg=30.0)
    
    config = AdvancedLayoutConfig(
        module_transforms={
            0: transform1,
            5: transform2,
            10: transform3
        }
    )
    
    assert len(config.module_transforms) == 3
    assert config.module_transforms[0].azimuth_deg == 90.0
    assert config.module_transforms[5].azimuth_deg == 180.0
    assert config.module_transforms[10].azimuth_deg == 270.0
    
    print("✓ AdvancedLayoutConfig mit ModuleTransforms erfolgreich erstellt")


def test_advanced_layout_config_with_groups():
    """Test: AdvancedLayoutConfig mit ModuleGroups"""
    print("\nTest 3: AdvancedLayoutConfig mit ModuleGroups...")
    
    # Erstelle einige Gruppen
    group1 = ModuleGroup(
        name="south_roof",
        module_indices=[0, 1, 2, 3],
        azimuth_deg=0.0,
        tilt_deg=30.0
    )
    group2 = ModuleGroup(
        name="east_roof",
        module_indices=[10, 11, 12],
        azimuth_deg=270.0,
        tilt_deg=25.0
    )
    
    config = AdvancedLayoutConfig(
        module_groups={
            "south_roof": group1,
            "east_roof": group2
        }
    )
    
    assert len(config.module_groups) == 2
    assert config.module_groups["south_roof"].get_module_count() == 4
    assert config.module_groups["east_roof"].get_module_count() == 3
    
    print("✓ AdvancedLayoutConfig mit ModuleGroups erfolgreich erstellt")


def test_mounting_modes():
    """Test: Verschiedene Aufständerungs-Modi"""
    print("\nTest 4: Aufständerungs-Modi...")
    
    # Süd-Aufständerung
    config1 = AdvancedLayoutConfig(mounting_mode="south")
    assert config1.mounting_mode == "south"
    
    # Ost-West-Aufständerung
    config2 = AdvancedLayoutConfig(mounting_mode="east-west")
    assert config2.mounting_mode == "east-west"
    
    # Süd-Ost-Aufständerung
    config3 = AdvancedLayoutConfig(mounting_mode="south-east")
    assert config3.mounting_mode == "south-east"
    
    # Süd-West-Aufständerung
    config4 = AdvancedLayoutConfig(mounting_mode="south-west")
    assert config4.mounting_mode == "south-west"
    
    # Individuell mit benutzerdefinierten Werten
    config5 = AdvancedLayoutConfig(
        mounting_mode="custom",
        custom_azimuth=135.0,
        custom_tilt=20.0
    )
    assert config5.mounting_mode == "custom"
    assert config5.custom_azimuth == 135.0
    assert config5.custom_tilt == 20.0
    
    print("✓ Alle Aufständerungs-Modi funktionieren korrekt")


def test_feature_flags():
    """Test: Feature-Flags (Kollisionserkennung, Verschattungs-Analyse)"""
    print("\nTest 5: Feature-Flags...")
    
    # Standardwerte
    config1 = AdvancedLayoutConfig()
    assert config1.enable_collision_detection is True
    assert config1.enable_shading_analysis is False
    
    # Benutzerdefinierte Werte
    config2 = AdvancedLayoutConfig(
        enable_collision_detection=False,
        enable_shading_analysis=True
    )
    assert config2.enable_collision_detection is False
    assert config2.enable_shading_analysis is True
    
    print("✓ Feature-Flags funktionieren korrekt")


def test_to_json():
    """Test: Serialisierung zu JSON"""
    print("\nTest 6: to_json() Methode...")
    
    # Erstelle komplexe Konfiguration
    transform1 = ModuleTransform(index=0, azimuth_deg=90.0, tilt_deg=20.0)
    transform2 = ModuleTransform(index=5, azimuth_deg=180.0, tilt_deg=25.0)
    
    group1 = ModuleGroup(
        name="test_group",
        module_indices=[0, 1, 2],
        azimuth_deg=45.0,
        tilt_deg=30.0
    )
    
    config = AdvancedLayoutConfig(
        mode="manual",
        use_garage=True,
        use_facade=True,
        removed_indices=[3, 4],
        module_transforms={0: transform1, 5: transform2},
        module_groups={"test_group": group1},
        mounting_mode="custom",
        custom_azimuth=135.0,
        custom_tilt=22.5,
        enable_collision_detection=False,
        enable_shading_analysis=True
    )
    
    json_str = config.to_json()
    
    # Prüfe dass JSON-String erstellt wurde
    assert isinstance(json_str, str)
    assert len(json_str) > 0
    
    # Prüfe dass wichtige Felder enthalten sind
    assert '"mode"' in json_str
    assert '"module_transforms"' in json_str
    assert '"module_groups"' in json_str
    assert '"mounting_mode"' in json_str
    assert '"custom_azimuth"' in json_str
    
    print(f"  JSON-Länge: {len(json_str)} Zeichen")
    print("✓ to_json() funktioniert korrekt")


def test_from_json():
    """Test: Deserialisierung aus JSON"""
    print("\nTest 7: from_json() Methode...")
    
    # Erstelle JSON-String
    json_str = '''
    {
        "mode": "manual",
        "use_garage": true,
        "use_facade": false,
        "removed_indices": [1, 2, 3],
        "garage_dims": [7.0, 4.0, 3.5],
        "offset_main_xy": [0.5, 0.5],
        "offset_garage_xy": [1.0, 0.0],
        "module_transforms": {
            "0": {
                "index": 0,
                "azimuth_deg": 90.0,
                "tilt_deg": 20.0,
                "offset_x": 0.0,
                "offset_y": 0.0,
                "offset_z": 0.0,
                "group_id": null
            }
        },
        "module_groups": {
            "test_group": {
                "name": "test_group",
                "module_indices": [5, 6, 7],
                "azimuth_deg": 180.0,
                "tilt_deg": 25.0,
                "color": "#ff0000"
            }
        },
        "mounting_mode": "east-west",
        "custom_azimuth": 45.0,
        "custom_tilt": 18.0,
        "enable_collision_detection": false,
        "enable_shading_analysis": true
    }
    '''
    
    config = AdvancedLayoutConfig.from_json(json_str)
    
    # Prüfe Basis-Felder
    assert config.mode == "manual"
    assert config.use_garage is True
    assert config.use_facade is False
    assert config.removed_indices == [1, 2, 3]
    assert config.garage_dims == (7.0, 4.0, 3.5)
    
    # Prüfe erweiterte Felder
    assert len(config.module_transforms) == 1
    assert 0 in config.module_transforms
    assert config.module_transforms[0].azimuth_deg == 90.0
    
    assert len(config.module_groups) == 1
    assert "test_group" in config.module_groups
    assert config.module_groups["test_group"].get_module_count() == 3
    
    assert config.mounting_mode == "east-west"
    assert config.custom_azimuth == 45.0
    assert config.custom_tilt == 18.0
    assert config.enable_collision_detection is False
    assert config.enable_shading_analysis is True
    
    print("✓ from_json() funktioniert korrekt")


def test_from_json_with_defaults():
    """Test: from_json() mit minimalen Daten"""
    print("\nTest 8: from_json() mit Standardwerten...")
    
    # Minimaler JSON-String
    json_str = '{}'
    
    config = AdvancedLayoutConfig.from_json(json_str)
    
    # Prüfe dass Standardwerte verwendet werden
    assert config.mode == "auto"
    assert config.use_garage is False
    assert config.module_transforms == {}
    assert config.module_groups == {}
    assert config.mounting_mode == "south"
    assert config.enable_collision_detection is True
    
    print("✓ from_json() mit Standardwerten funktioniert korrekt")


def test_roundtrip():
    """Test: Roundtrip to_json() -> from_json()"""
    print("\nTest 9: Roundtrip to_json() -> from_json()...")
    
    # Erstelle komplexe Original-Konfiguration
    transform1 = ModuleTransform(
        index=0,
        azimuth_deg=90.0,
        tilt_deg=20.0,
        offset_x=1.5,
        offset_y=-0.5,
        offset_z=0.2
    )
    transform2 = ModuleTransform(
        index=10,
        azimuth_deg=270.0,
        tilt_deg=35.0
    )
    
    group1 = ModuleGroup(
        name="south_roof",
        module_indices=[0, 1, 2, 3, 4],
        azimuth_deg=0.0,
        tilt_deg=30.0,
        color="#00ff00"
    )
    group2 = ModuleGroup(
        name="west_roof",
        module_indices=[10, 11, 12],
        azimuth_deg=90.0,
        tilt_deg=25.0,
        color="#0000ff"
    )
    
    original = AdvancedLayoutConfig(
        mode="manual",
        use_garage=True,
        use_facade=True,
        removed_indices=[5, 6, 7],
        garage_dims=(8.0, 4.5, 3.2),
        offset_main_xy=(0.3, 0.4),
        offset_garage_xy=(1.2, 0.8),
        module_transforms={0: transform1, 10: transform2},
        module_groups={"south_roof": group1, "west_roof": group2},
        mounting_mode="custom",
        custom_azimuth=135.0,
        custom_tilt=22.5,
        enable_collision_detection=False,
        enable_shading_analysis=True
    )
    
    # Konvertiere zu JSON und zurück
    json_str = original.to_json()
    restored = AdvancedLayoutConfig.from_json(json_str)
    
    # Vergleiche Basis-Felder
    assert restored.mode == original.mode
    assert restored.use_garage == original.use_garage
    assert restored.use_facade == original.use_facade
    assert restored.removed_indices == original.removed_indices
    assert restored.garage_dims == original.garage_dims
    
    # Vergleiche erweiterte Felder
    assert len(restored.module_transforms) == len(original.module_transforms)
    assert restored.module_transforms[0].azimuth_deg == 90.0
    assert restored.module_transforms[10].azimuth_deg == 270.0
    
    assert len(restored.module_groups) == len(original.module_groups)
    assert restored.module_groups["south_roof"].get_module_count() == 5
    assert restored.module_groups["west_roof"].get_module_count() == 3
    
    assert restored.mounting_mode == original.mounting_mode
    assert restored.custom_azimuth == original.custom_azimuth
    assert restored.custom_tilt == original.custom_tilt
    assert restored.enable_collision_detection == original.enable_collision_detection
    assert restored.enable_shading_analysis == original.enable_shading_analysis
    
    print("✓ Roundtrip funktioniert korrekt")


def test_inheritance():
    """Test: Vererbung von LayoutConfig"""
    print("\nTest 10: Vererbung von LayoutConfig...")
    
    from utils.pv3d import LayoutConfig
    
    config = AdvancedLayoutConfig()
    
    # Prüfe dass AdvancedLayoutConfig von LayoutConfig erbt
    assert isinstance(config, LayoutConfig)
    assert isinstance(config, AdvancedLayoutConfig)
    
    # Prüfe dass Basis-Methoden verfügbar sind
    assert hasattr(config, 'to_json')
    assert hasattr(config, 'from_json')
    
    print("✓ Vererbung funktioniert korrekt")


def main():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("AdvancedLayoutConfig Tests (Task 11.3)")
    print("=" * 70)
    
    try:
        test_advanced_layout_config_creation()
        test_advanced_layout_config_with_transforms()
        test_advanced_layout_config_with_groups()
        test_mounting_modes()
        test_feature_flags()
        test_to_json()
        test_from_json()
        test_from_json_with_defaults()
        test_roundtrip()
        test_inheritance()
        
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
