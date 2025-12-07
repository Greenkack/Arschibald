"""
Comprehensive Test für Export-Funktionen (Task 9)

Testet alle Export-Funktionen gemäß Task 9:
- Screenshot-Export in verschiedenen Formaten (PNG, JPEG)
- Multi-View Export als ZIP
- 360° Animation Export als GIF
- 3D-Modell Export (STL, GLTF, OBJ)
"""

import os
import sys
import zipfile

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


def test_screenshot_png():
    """Test Screenshot-Export in PNG Format"""
    print("\n" + "="*60)
    print("TEST 1: Screenshot Export - PNG Format")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        png_bytes = export_screenshot_from_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            format="png",
            width=1600,
            height=1000
        )
        
        if png_bytes and len(png_bytes) > 0:
            # Speichere Datei
            with open("test_screenshot_png.png", "wb") as f:
                f.write(png_bytes)
            
            print(f"PNG Screenshot erstellt ({len(png_bytes)} bytes)")
            print("Datei gespeichert: test_screenshot_png.png")
            return True
        else:
            print("PNG Screenshot ist leer")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        return False


def test_screenshot_jpeg():
    """Test Screenshot-Export in JPEG Format"""
    print("\n" + "="*60)
    print("TEST 2: Screenshot Export - JPEG Format")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        jpeg_bytes = export_screenshot_from_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=15,
            format="jpeg",
            width=1600,
            height=1000
        )
        
        if jpeg_bytes and len(jpeg_bytes) > 0:
            # Speichere Datei
            with open("test_screenshot_jpeg.jpg", "wb") as f:
                f.write(jpeg_bytes)
            
            print(f"JPEG Screenshot erstellt ({len(jpeg_bytes)} bytes)")
            print("Datei gespeichert: test_screenshot_jpeg.jpg")
            return True
        else:
            print("JPEG Screenshot ist leer")
            return False
            
    except Exception as e:
        print(f"Fehler: {e}")
        return False


def test_multi_view_zip():
    """Test Multi-View Export als ZIP"""
    print("\n" + "="*60)
    print("TEST 3: Multi-View Export als ZIP")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=12.0, width_m=8.0, wall_height_m=3.5)
        
        # Teste mit allen Standard-Views
        views_dict = export_multi_view(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=25,
            views=["isometric", "top", "south", "east"],
            resolution=(1200, 750),
            return_zip_bytes=True
        )
        
        if not views_dict or len(views_dict) == 0:
            print("Keine Views erstellt")
            return False
        
        # Prüfe einzelne Views
        view_count = len([k for k in views_dict.keys() if k != "_zip"])
        print(f"{view_count} Views erstellt")
        
        # Prüfe ZIP-Datei
        if "_zip" not in views_dict:
            print("Keine ZIP-Datei erstellt")
            return False
        
        zip_bytes = views_dict["_zip"]
        print(f"ZIP-Datei erstellt ({len(zip_bytes)} bytes)")
        
        # Speichere und validiere ZIP
        zip_path = "test_multi_view_export.zip"
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)
        
        # Prüfe ZIP-Inhalt
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            files = zipf.namelist()
            print(f"ZIP enthält {len(files)} Dateien:")
            for filename in files:
                file_info = zipf.getinfo(filename)
                print(f"  - {filename} ({file_info.file_size} bytes)")
        
        print(f"ZIP gespeichert: {zip_path}")
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_360_animation_gif():
    """Test 360° Animation Export als GIF"""
    print("\n" + "="*60)
    print("TEST 4: 360° Animation Export als GIF")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        
        # Teste mit 18 Frames (schneller als 36)
        gif_path = "test_360_animation_export.gif"
        gif_bytes = export_360_animation(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            filepath=gif_path,
            frames=18,
            resolution=(800, 600),
            duration_ms=100,
            return_bytes=True
        )
        
        if not gif_bytes or len(gif_bytes) == 0:
            print("GIF Animation ist leer")
            return False
        
        print(f"GIF Animation erstellt ({len(gif_bytes)} bytes)")
        
        # Prüfe ob Datei existiert
        if not os.path.exists(gif_path):
            print("GIF-Datei wurde nicht gespeichert")
            return False
        
        file_size = os.path.getsize(gif_path)
        print(f"GIF gespeichert: {gif_path} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3d_model_stl():
    """Test 3D-Modell Export - STL Format"""
    print("\n" + "="*60)
    print("TEST 5: 3D-Modell Export - STL Format")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        layout = LayoutConfig(mode="auto")
        
        stl_path = "test_export_flat.stl"
        success = export_3d_model(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=15,
            layout_config=layout,
            filepath=stl_path,
            format="stl"
        )
        
        if not success:
            print("STL Export fehlgeschlagen")
            return False
        
        # Prüfe Datei
        if not os.path.exists(stl_path):
            print("STL-Datei wurde nicht erstellt")
            return False
        
        file_size = os.path.getsize(stl_path)
        print(f"STL Export erfolgreich: {stl_path} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3d_model_gltf():
    """Test 3D-Modell Export - GLTF Format"""
    print("\n" + "="*60)
    print("TEST 6: 3D-Modell Export - GLTF/GLB Format")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        layout = LayoutConfig(mode="auto")
        
        glb_path = "test_export_gable.glb"
        success = export_3d_model(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            layout_config=layout,
            filepath=glb_path,
            format="glb"
        )
        
        if not success:
            print("GLB Export fehlgeschlagen")
            return False
        
        # Prüfe Datei
        if not os.path.exists(glb_path):
            print("GLB-Datei wurde nicht erstellt")
            return False
        
        file_size = os.path.getsize(glb_path)
        print(f"GLB Export erfolgreich: {glb_path} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3d_model_obj():
    """Test 3D-Modell Export - OBJ Format"""
    print("\n" + "="*60)
    print("TEST 7: 3D-Modell Export - OBJ Format")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=3.0)
        layout = LayoutConfig(mode="auto")
        
        obj_path = "test_export_hip.obj"
        success = export_3d_model(
            project_data=project_data,
            dims=dims,
            roof_type="Walmdach",
            module_quantity=18,
            layout_config=layout,
            filepath=obj_path,
            format="obj"
        )
        
        if not success:
            print("OBJ Export fehlgeschlagen")
            return False
        
        # Prüfe Datei
        if not os.path.exists(obj_path):
            print("OBJ-Datei wurde nicht erstellt")
            return False
        
        file_size = os.path.getsize(obj_path)
        print(f"OBJ Export erfolgreich: {obj_path} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_formats_export():
    """Test Export aller Formate auf einmal"""
    print("\n" + "="*60)
    print("TEST 8: Export aller 3D-Formate (STL, GLB, OBJ)")
    print("="*60)
    
    try:
        project_data = {}
        dims = BuildingDims(length_m=12.0, width_m=8.0, wall_height_m=3.5)
        layout = LayoutConfig(mode="auto")
        
        results = export_all_formats(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=25,
            layout_config=layout,
            output_dir=".",
            base_filename="test_all_formats"
        )
        
        if not results:
            print("Keine Formate exportiert")
            return False
        
        print(f"{len(results)} Formate exportiert:")
        
        all_success = True
        for fmt, success in results.items():
            status = "" if success else ""
            print(f"  {status} {fmt.upper()}: {'Erfolgreich' if success else 'Fehlgeschlagen'}")
            
            if success:
                filepath = f"test_all_formats.{fmt}"
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    print(f"    Datei: {filepath} ({file_size} bytes)")
            
            all_success = all_success and success
        
        return all_success
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führe alle Export-Tests aus"""
    print("\n" + "="*60)
    print("COMPREHENSIVE EXPORT FUNCTIONS TESTS (TASK 9)")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("\nPV3D nicht verfügbar - Tests können nicht ausgeführt werden")
        return 1
    
    results = []
    
    # Test 1: Screenshot PNG
    results.append(("Screenshot Export - PNG", test_screenshot_png()))
    
    # Test 2: Screenshot JPEG
    results.append(("Screenshot Export - JPEG", test_screenshot_jpeg()))
    
    # Test 3: Multi-View ZIP
    results.append(("Multi-View Export als ZIP", test_multi_view_zip()))
    
    # Test 4: 360° Animation GIF
    results.append(("360° Animation Export als GIF", test_360_animation_gif()))
    
    # Test 5: 3D Model STL
    results.append(("3D-Modell Export - STL", test_3d_model_stl()))
    
    # Test 6: 3D Model GLTF
    results.append(("3D-Modell Export - GLTF/GLB", test_3d_model_gltf()))
    
    # Test 7: 3D Model OBJ
    results.append(("3D-Modell Export - OBJ", test_3d_model_obj()))
    
    # Test 8: All Formats
    results.append(("Export aller Formate", test_all_formats_export()))
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("TEST ZUSAMMENFASSUNG - TASK 9")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\nTask 9 Sub-Tasks:")
    print("  Teste Screenshot-Export in verschiedenen Formaten")
    print("  Teste Multi-View Export als ZIP")
    print("  Teste 360° Animation Export als GIF")
    print("  Teste 3D-Modell Export (STL, GLTF, OBJ)")
    
    print("\nTest Ergebnisse:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE EXPORT-TESTS BESTANDEN!")
        print("\nTask 9 erfolgreich abgeschlossen:")
        print("   - Screenshot-Export in PNG und JPEG funktioniert")
        print("   - Multi-View Export als ZIP funktioniert")
        print("   - 360° Animation Export als GIF funktioniert")
        print("   - 3D-Modell Export in STL, GLTF und OBJ funktioniert")
        return 0
    else:
        print(f"\n{total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
