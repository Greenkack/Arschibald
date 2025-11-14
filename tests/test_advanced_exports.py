"""
Test für erweiterte Export-Funktionen (Task 18)

Testet die neu implementierten Export-Funktionen:
- CSV-Export
- JSON-Export/Import
- Multi-View Screenshots
- 360° Animation
"""

import sys
import os

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

def test_csv_export():
    """Test CSV-Export Funktion"""
    print("\n=== Test 1: CSV-Export ===")
    
    try:
        from pv3d import export_module_details_csv, ModuleTransform
        
        # Erstelle Test-Daten
        module_transforms = {
            0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=15.0, group_id="Süddach"),
            1: ModuleTransform(index=1, azimuth_deg=90.0, tilt_deg=20.0, group_id="Westdach"),
            2: ModuleTransform(index=2, azimuth_deg=0.0, tilt_deg=15.0)
        }
        
        module_positions = [
            (0.0, 0.0, 6.0),
            (2.0, 0.0, 6.0),
            (4.0, 0.0, 6.0)
        ]
        
        shading_values = {
            0: 0.0,
            1: 25.5,
            2: 50.0
        }
        
        # Exportiere CSV
        csv_string = export_module_details_csv(
            module_transforms=module_transforms,
            module_positions=module_positions,
            shading_values=shading_values,
            filepath=None
        )
        
        # Validiere CSV
        assert csv_string is not None, "CSV-String ist None"
        assert "Index,X,Y,Z,Azimuth,Tilt,Group,Shading%" in csv_string, "CSV-Header fehlt"
        assert "0,0.00,0.00,6.00,0.0,15.0,Süddach,0.0" in csv_string, "Modul 0 Daten fehlen"
        assert "1,2.00,0.00,6.00,90.0,20.0,Westdach,25.5" in csv_string, "Modul 1 Daten fehlen"
        
        print("[OK] CSV-Export funktioniert korrekt")
        print(f"  - CSV-Länge: {len(csv_string)} Zeichen")
        print(f"  - Anzahl Zeilen: {len(csv_string.splitlines())}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] CSV-Export fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_export_import():
    """Test JSON-Export/Import Funktionen"""
    print("\n=== Test 2: JSON-Export/Import ===")
    
    try:
        from pv3d import (
            export_layout_json,
            import_layout_json,
            AdvancedLayoutConfig,
            ModuleTransform,
            ModuleGroup
        )
        
        # Erstelle Test-Konfiguration
        config = AdvancedLayoutConfig(
            mode="manual",
            use_garage=True,
            use_facade=False,
            removed_indices=[0, 1, 5],
            mounting_mode="south-east",
            custom_azimuth=45.0,
            custom_tilt=20.0,
            enable_collision_detection=True,
            enable_shading_analysis=False
        )
        
        # Füge Modul-Transformationen hinzu
        config.module_transforms[0] = ModuleTransform(
            index=0,
            azimuth_deg=0.0,
            tilt_deg=15.0,
            group_id="test_group"
        )
        
        # Füge Modul-Gruppe hinzu
        config.module_groups["test_group"] = ModuleGroup(
            name="test_group",
            module_indices=[0, 1, 2],
            azimuth_deg=0.0,
            tilt_deg=15.0
        )
        
        # Exportiere JSON
        json_string = export_layout_json(config, filepath=None)
        
        # Validiere JSON
        assert json_string is not None, "JSON-String ist None"
        assert "mounting_mode" in json_string, "mounting_mode fehlt in JSON"
        assert "south-east" in json_string, "mounting_mode Wert fehlt"
        
        print("[OK] JSON-Export funktioniert korrekt")
        print(f"  - JSON-Länge: {len(json_string)} Zeichen")
        
        # Importiere JSON
        imported_config = import_layout_json(json_string=json_string)
        
        # Validiere Import
        assert imported_config.mode == "manual", "Mode nicht korrekt importiert"
        assert imported_config.mounting_mode == "south-east", "mounting_mode nicht korrekt importiert"
        assert imported_config.custom_azimuth == 45.0, "custom_azimuth nicht korrekt importiert"
        assert 0 in imported_config.module_transforms, "module_transforms nicht importiert"
        assert "test_group" in imported_config.module_groups, "module_groups nicht importiert"
        
        print("[OK] JSON-Import funktioniert korrekt")
        print(f"  - Mode: {imported_config.mode}")
        print(f"  - Mounting Mode: {imported_config.mounting_mode}")
        print(f"  - Module Transforms: {len(imported_config.module_transforms)}")
        print(f"  - Module Groups: {len(imported_config.module_groups)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] JSON-Export/Import fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_function_signatures():
    """Test ob alle Export-Funktionen existieren und korrekte Signaturen haben"""
    print("\n=== Test 3: Funktions-Signaturen ===")
    
    try:
        from pv3d import (
            export_module_details_csv,
            export_layout_json,
            import_layout_json,
            export_multi_view_screenshots,
            export_360_animation
        )
        
        # Prüfe ob Funktionen callable sind
        assert callable(export_module_details_csv), "export_module_details_csv nicht callable"
        assert callable(export_layout_json), "export_layout_json nicht callable"
        assert callable(import_layout_json), "import_layout_json nicht callable"
        assert callable(export_multi_view_screenshots), "export_multi_view_screenshots nicht callable"
        assert callable(export_360_animation), "export_360_animation nicht callable"
        
        print("[OK] Alle Export-Funktionen existieren")
        print("  - export_module_details_csv")
        print("  - export_layout_json")
        print("  - import_layout_json")
        print("  - export_multi_view_screenshots")
        print("  - export_360_animation")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Funktions-Signaturen Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("TASK 18: Erweiterte Export-Funktionen - Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: CSV-Export
    results.append(("CSV-Export", test_csv_export()))
    
    # Test 2: JSON-Export/Import
    results.append(("JSON-Export/Import", test_json_export_import()))
    
    # Test 3: Funktions-Signaturen
    results.append(("Funktions-Signaturen", test_function_signatures()))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{name:30s} {status}")
    
    print("-" * 60)
    print(f"Gesamt: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n[OK] ALLE TESTS BESTANDEN!")
        return 0
    else:
        print(f"\n[ERROR] {total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
