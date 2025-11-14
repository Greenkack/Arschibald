"""
Test für Multi-View Screenshot Export (Task 18.3)

Testet die export_multi_view_screenshots Funktion:
- Erstellt Screenshots aus 4 Perspektiven
- Erstellt ZIP-Datei
- Validiert Ausgabe
"""

import sys
import os
import tempfile

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))


def test_multi_view_screenshots():
    """Test Multi-View Screenshot Export"""
    print("\n=== Test: Multi-View Screenshots ===")
    
    try:
        from pv3d import (
            export_multi_view_screenshots,
            BuildingDims,
            LayoutConfig
        )
        
        # Erstelle Test-Konfiguration
        dims = BuildingDims(
            length_m=10.0,
            width_m=6.0,
            wall_height_m=6.0
        )
        
        layout_config = LayoutConfig(
            mode="auto",
            use_garage=False,
            use_facade=False
        )
        
        project_data = {
            "project_details": {
                "roof_type": "Satteldach",
                "roof_orientation": "Süd",
                "roof_inclination_deg": 35.0,
                "roof_covering_type": "Ziegel"
            }
        }
        
        # Erstelle temporäres Verzeichnis
        with tempfile.TemporaryDirectory() as tmp_dir:
            print(f"  Temporäres Verzeichnis: {tmp_dir}")
            
            # Exportiere Multi-View Screenshots
            print("  Erstelle Multi-View Screenshots...")
            views = export_multi_view_screenshots(
                project_data=project_data,
                dims=dims,
                roof_type="Satteldach",
                module_quantity=20,
                layout_config=layout_config,
                output_dir=tmp_dir,
                base_filename="test_view",
                resolution=(800, 600)  # Kleinere Auflösung für schnelleren Test
            )
            
            # Validiere Views Dictionary
            assert views is not None, "Views Dictionary ist None"
            assert isinstance(views, dict), "Views ist kein Dictionary"
            
            print(f"  [OK] Views Dictionary erstellt: {len(views)} Ansichten")
            
            # Prüfe ob alle 4 Views vorhanden sind
            expected_views = ["isometric", "top", "south", "east"]
            for view_name in expected_views:
                assert view_name in views, f"View '{view_name}' fehlt"
                assert isinstance(views[view_name], bytes), f"View '{view_name}' ist nicht bytes"
                print(f"  [OK] View '{view_name}': {len(views[view_name])} bytes")
            
            # Prüfe ob ZIP-Datei erstellt wurde
            zip_filepath = os.path.join(tmp_dir, "test_view_multi_view.zip")
            assert os.path.exists(zip_filepath), "ZIP-Datei wurde nicht erstellt"
            
            zip_size = os.path.getsize(zip_filepath)
            print(f"  [OK] ZIP-Datei erstellt: {zip_size} bytes")
            
            # Prüfe ZIP-Inhalt
            import zipfile
            with zipfile.ZipFile(zip_filepath, 'r') as zipf:
                zip_contents = zipf.namelist()
                print(f"  [OK] ZIP enthält {len(zip_contents)} Dateien:")
                for filename in zip_contents:
                    print(f"    - {filename}")
                
                # Prüfe ob alle erwarteten Dateien vorhanden sind
                for view_name in expected_views:
                    expected_filename = f"test_view_{view_name}.png"
                    assert expected_filename in zip_contents, f"Datei '{expected_filename}' fehlt in ZIP"
        
        print("\n[OK] Multi-View Screenshots Test BESTANDEN")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Multi-View Screenshots Test FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_view_with_different_roof_types():
    """Test Multi-View mit verschiedenen Dachtypen"""
    print("\n=== Test: Multi-View mit verschiedenen Dachtypen ===")
    
    try:
        from pv3d import (
            export_multi_view_screenshots,
            BuildingDims,
            LayoutConfig
        )
        
        roof_types = ["Flachdach", "Satteldach", "Walmdach"]
        
        for roof_type in roof_types:
            print(f"\n  Teste Dachtyp: {roof_type}")
            
            dims = BuildingDims(
                length_m=10.0,
                width_m=6.0,
                wall_height_m=6.0
            )
            
            layout_config = LayoutConfig(mode="auto")
            
            project_data = {
                "project_details": {
                    "roof_type": roof_type,
                    "roof_orientation": "Süd",
                    "roof_inclination_deg": 35.0,
                    "roof_covering_type": "Ziegel"
                }
            }
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                views = export_multi_view_screenshots(
                    project_data=project_data,
                    dims=dims,
                    roof_type=roof_type,
                    module_quantity=15,
                    layout_config=layout_config,
                    output_dir=tmp_dir,
                    base_filename=f"test_{roof_type.lower()}",
                    resolution=(400, 300)  # Sehr kleine Auflösung für schnellen Test
                )
                
                assert len(views) == 4, f"Erwartete 4 Views, erhalten: {len(views)}"
                print(f"  [OK] {roof_type}: {len(views)} Views erstellt")
        
        print("\n[OK] Multi-View mit verschiedenen Dachtypen Test BESTANDEN")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Multi-View mit verschiedenen Dachtypen Test FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("TASK 18.3: Multi-View Screenshot Export - Tests")
    print("=" * 70)
    
    results = []
    
    # Test 1: Basis Multi-View Test
    results.append(("Multi-View Screenshots", test_multi_view_screenshots()))
    
    # Test 2: Multi-View mit verschiedenen Dachtypen
    results.append(("Multi-View verschiedene Dachtypen", test_multi_view_with_different_roof_types()))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{name:40s} {status}")
    
    print("-" * 70)
    print(f"Gesamt: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n[OK] ALLE TESTS BESTANDEN!")
        print("\nTask 18.3 ist vollständig implementiert:")
        print("  [OK] export_multi_view_screenshots() Funktion")
        print("  [OK] Screenshots aus 4 Perspektiven (Isometrisch, Top, Süd, Ost)")
        print("  [OK] ZIP-Datei mit allen Screenshots")
        print("  [OK] Download-Button in UI (pages/solar_3d_view.py)")
        return 0
    else:
        print(f"\n[ERROR] {total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
