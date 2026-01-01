"""
Test für PV3D Export Module

Testet alle Export-Funktionen des pv3d_export Moduls.
"""

import os
import sys

# Füge aktuelles Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.pv3d_export import (
        export_screenshot,
        export_screenshot_from_scene,
        export_multi_view,
        export_360_animation,
        export_3d_model,
        export_all_formats,
        PV3D_AVAILABLE
    )
    from utils.pv3d import BuildingDims, LayoutConfig
    from utils.pv3d_plotly import build_plotly_scene
    
    print("Alle Imports erfolgreich")
    
except ImportError as e:
    print(f"Import-Fehler: {e}")
    sys.exit(1)


def test_module_availability():
    """Test ob PV3D verfügbar ist"""
    print("\n" + "="*60)
    print("TEST 1: Module Verfügbarkeit")
    print("="*60)
    
    if PV3D_AVAILABLE:
        print("PV3D ist verfügbar")
        return True
    else:
        print("PV3D ist nicht verfügbar")
        return False


def test_screenshot_export():
    """Test Screenshot Export"""
    print("\n" + "="*60)
    print("TEST 2: Screenshot Export")
    print("="*60)
    
    try:
        # Erstelle Test-Daten
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        # Erstelle Figure
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=None,
            selected_modules=[]
        )
        
        # Exportiere Screenshot
        png_bytes = export_screenshot(fig, format="png", width=800, height=600)
        
        if png_bytes and len(png_bytes) > 0:
            print(f"Screenshot erstellt ({len(png_bytes)} bytes)")
            
            # Speichere zu Testzwecken
            with open("test_screenshot_export.png", "wb") as f:
                f.write(png_bytes)
            print("Screenshot gespeichert: test_screenshot_export.png")
            
            return True
        else:
            print("Screenshot ist leer")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_screenshot_from_scene():
    """Test Screenshot direkt aus Szene"""
    print("\n" + "="*60)
    print("TEST 3: Screenshot from Scene")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        png_bytes = export_screenshot_from_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=15,
            format="png",
            width=800,
            height=600
        )
        
        if png_bytes and len(png_bytes) > 0:
            print(f"Screenshot erstellt ({len(png_bytes)} bytes)")
            return True
        else:
            print("Screenshot ist leer")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_view_export():
    """Test Multi-View Export"""
    print("\n" + "="*60)
    print("TEST 4: Multi-View Export")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        # Teste mit nur 2 Views für Geschwindigkeit
        views_dict = export_multi_view(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            views=["isometric", "top"],
            resolution=(600, 400),
            return_zip_bytes=True
        )
        
        if views_dict and len(views_dict) > 0:
            print(f"Multi-View erstellt ({len(views_dict)} Ansichten)")
            
            # Prüfe ob ZIP-Bytes vorhanden sind
            if "_zip" in views_dict:
                zip_bytes = views_dict["_zip"]
                print(f"ZIP erstellt ({len(zip_bytes)} bytes)")
                
                # Speichere ZIP zu Testzwecken
                with open("test_multi_view.zip", "wb") as f:
                    f.write(zip_bytes)
                print("ZIP gespeichert: test_multi_view.zip")
            
            return True
        else:
            print("Keine Views erstellt")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_360_animation():
    """Test 360° Animation"""
    print("\n" + "="*60)
    print("TEST 5: 360° Animation")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        # Teste mit wenigen Frames für Geschwindigkeit
        gif_bytes = export_360_animation(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            filepath="test_animation_360.gif",
            frames=12,  # Nur 12 Frames für schnellen Test
            resolution=(400, 300),
            return_bytes=True
        )
        
        if gif_bytes and len(gif_bytes) > 0:
            print(f"Animation erstellt ({len(gif_bytes)} bytes)")
            print("Animation gespeichert: test_animation_360.gif")
            return True
        else:
            print("Animation ist leer")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3d_model_export():
    """Test 3D Model Export"""
    print("\n" + "="*60)
    print("TEST 6: 3D Model Export (STL)")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        layout = LayoutConfig(mode="auto")
        
        success = export_3d_model(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=10,
            layout_config=layout,
            filepath="test_export_module.stl",
            format="stl"
        )
        
        if success:
            print("STL Export erfolgreich")
            
            # Prüfe ob Datei existiert
            if os.path.exists("test_export_module.stl"):
                file_size = os.path.getsize("test_export_module.stl")
                print(f"Datei erstellt: test_export_module.stl ({file_size} bytes)")
                return True
            else:
                print("Datei wurde nicht erstellt")
                return False
        else:
            print("STL Export fehlgeschlagen")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("PV3D EXPORT MODULE TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Module Verfügbarkeit
    results.append(("Module Verfügbarkeit", test_module_availability()))
    
    if not PV3D_AVAILABLE:
        print("\nPV3D nicht verfügbar - überspringe weitere Tests")
        return
    
    # Test 2: Screenshot Export
    results.append(("Screenshot Export", test_screenshot_export()))
    
    # Test 3: Screenshot from Scene
    results.append(("Screenshot from Scene", test_screenshot_from_scene()))
    
    # Test 4: Multi-View Export
    results.append(("Multi-View Export", test_multi_view_export()))
    
    # Test 5: 360° Animation
    results.append(("360° Animation", test_360_animation()))
    
    # Test 6: 3D Model Export
    results.append(("3D Model Export", test_3d_model_export()))
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("TEST ZUSAMMENFASSUNG")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n ALLE TESTS BESTANDEN!")
        return 0
    else:
        print(f"\n{total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
