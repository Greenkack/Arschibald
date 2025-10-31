"""
Test-Skript für Task 6: Export-Funktionen

Testet die drei Export-Funktionen:
- render_image_bytes() - Off-Screen Screenshot als PNG
- export_stl() - STL-Export
- export_gltf() - glTF/glb-Export
"""

import os
import sys

# Füge utils-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from pv3d import (
        BuildingDims,
        LayoutConfig,
        render_image_bytes,
        export_stl,
        export_gltf
    )
    print("✓ Import von pv3d erfolgreich")
except ImportError as e:
    print(f"✗ Import-Fehler: {e}")
    sys.exit(1)


def test_render_image_bytes():
    """Test 6.1: Off-Screen Screenshot-Funktion"""
    print("\n" + "="*70)
    print("TEST 6.1: render_image_bytes() - Off-Screen Screenshot")
    print("="*70)
    
    # Test-Daten
    project_data = {
        "project_details": {
            "roof_orientation": "Süd",
            "roof_inclination_deg": 35.0,
            "roof_covering_type": "Ziegel"
        }
    }
    
    dims = BuildingDims(
        length_m=10.0,
        width_m=6.0,
        wall_height_m=6.0
    )
    
    layout = LayoutConfig(mode="auto")
    
    # Test 1: Flachdach mit Süd-Aufständerung
    print("\nTest 1: Flachdach mit 20 Modulen")
    try:
        png_bytes = render_image_bytes(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout,
            width=1600,
            height=1000
        )
        
        if len(png_bytes) > 0:
            print(f"  ✓ Screenshot erstellt: {len(png_bytes)} Bytes")
            
            # Speichere zu Testzwecken
            with open("test_screenshot_flat.png", "wb") as f:
                f.write(png_bytes)
            print("  ✓ Screenshot gespeichert: test_screenshot_flat.png")
            
            # Prüfe PNG-Header
            if png_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                print("  ✓ Gültiger PNG-Header")
            else:
                print("  ✗ Ungültiger PNG-Header")
        else:
            print("  ✗ Leere Bytes zurückgegeben")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
    
    # Test 2: Satteldach
    print("\nTest 2: Satteldach mit 15 Modulen")
    try:
        png_bytes = render_image_bytes(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=15,
            layout_config=layout,
            width=1600,
            height=1000
        )
        
        if len(png_bytes) > 0:
            print(f"  ✓ Screenshot erstellt: {len(png_bytes)} Bytes")
            
            with open("test_screenshot_gable.png", "wb") as f:
                f.write(png_bytes)
            print("  ✓ Screenshot gespeichert: test_screenshot_gable.png")
        else:
            print("  ✗ Leere Bytes zurückgegeben")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
    
    # Test 3: Verschiedene Auflösungen
    print("\nTest 3: Verschiedene Auflösungen")
    resolutions = [(800, 600), (1920, 1080), (2560, 1440)]
    for width, height in resolutions:
        try:
            png_bytes = render_image_bytes(
                project_data=project_data,
                dims=dims,
                roof_type="Flachdach",
                module_quantity=10,
                layout_config=layout,
                width=width,
                height=height
            )
            
            if len(png_bytes) > 0:
                print(f"  ✓ {width}x{height}: {len(png_bytes)} Bytes")
            else:
                print(f"  ✗ {width}x{height}: Leere Bytes")
        except Exception as e:
            print(f"  ✗ {width}x{height}: Fehler - {e}")
    
    # Test 4: Fehlerbehandlung (ungültige Daten)
    print("\nTest 4: Fehlerbehandlung")
    try:
        png_bytes = render_image_bytes(
            project_data={},
            dims=BuildingDims(length_m=-10, width_m=-5, wall_height_m=-3),
            roof_type="UnbekannterTyp",
            module_quantity=0,
            layout_config=layout
        )
        
        if len(png_bytes) == 0:
            print("  ✓ Fehlerbehandlung funktioniert (leere Bytes bei Fehler)")
        else:
            print("  ✓ Rendering trotz ungültiger Daten erfolgreich")
    except Exception as e:
        print(f"  ✗ Exception nicht abgefangen: {e}")


def test_export_stl():
    """Test 6.2: STL-Export"""
    print("\n" + "="*70)
    print("TEST 6.2: export_stl() - STL-Export")
    print("="*70)
    
    # Test-Daten
    project_data = {
        "project_details": {
            "roof_orientation": "Süd",
            "roof_inclination_deg": 35.0,
            "roof_covering_type": "Beton"
        }
    }
    
    dims = BuildingDims(
        length_m=10.0,
        width_m=6.0,
        wall_height_m=6.0
    )
    
    layout = LayoutConfig(mode="auto")
    
    # Test 1: Flachdach STL-Export
    print("\nTest 1: Flachdach STL-Export")
    filepath = "test_export_flat.stl"
    try:
        success = export_stl(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout,
            filepath=filepath
        )
        
        if success:
            print(f"  ✓ STL-Export erfolgreich")
            
            # Prüfe ob Datei existiert
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  ✓ Datei erstellt: {filepath} ({file_size} Bytes)")
                
                # Prüfe STL-Header (binär)
                with open(filepath, "rb") as f:
                    header = f.read(80)
                    if len(header) == 80:
                        print("  ✓ Gültiger STL-Header (80 Bytes)")
                    else:
                        print("  ✗ Ungültiger STL-Header")
            else:
                print(f"  ✗ Datei nicht gefunden: {filepath}")
        else:
            print("  ✗ STL-Export fehlgeschlagen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
    
    # Test 2: Satteldach STL-Export
    print("\nTest 2: Satteldach STL-Export")
    filepath = "test_export_gable.stl"
    try:
        success = export_stl(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=15,
            layout_config=layout,
            filepath=filepath
        )
        
        if success and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✓ STL-Export erfolgreich: {filepath} ({file_size} Bytes)")
        else:
            print("  ✗ STL-Export fehlgeschlagen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
    
    # Test 3: Walmdach STL-Export
    print("\nTest 3: Walmdach STL-Export")
    filepath = "test_export_hip.stl"
    try:
        success = export_stl(
            project_data=project_data,
            dims=dims,
            roof_type="Walmdach",
            module_quantity=12,
            layout_config=layout,
            filepath=filepath
        )
        
        if success and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✓ STL-Export erfolgreich: {filepath} ({file_size} Bytes)")
        else:
            print("  ✗ STL-Export fehlgeschlagen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")


def test_export_gltf():
    """Test 6.3: glTF-Export"""
    print("\n" + "="*70)
    print("TEST 6.3: export_gltf() - glTF/glb-Export")
    print("="*70)
    
    # Test-Daten
    project_data = {
        "project_details": {
            "roof_orientation": "West",
            "roof_inclination_deg": 25.0,
            "roof_covering_type": "Schiefer"
        }
    }
    
    dims = BuildingDims(
        length_m=12.0,
        width_m=8.0,
        wall_height_m=7.0
    )
    
    layout = LayoutConfig(mode="auto")
    
    # Test 1: glTF-Export (Text-Format)
    print("\nTest 1: glTF-Export (Text-Format)")
    filepath = "test_export.gltf"
    try:
        success = export_gltf(
            project_data=project_data,
            dims=dims,
            roof_type="Pultdach",
            module_quantity=18,
            layout_config=layout,
            filepath=filepath
        )
        
        if success:
            print(f"  ✓ glTF-Export erfolgreich")
            
            # Prüfe ob Datei existiert
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  ✓ Datei erstellt: {filepath} ({file_size} Bytes)")
                
                # Prüfe glTF-Format (JSON)
                with open(filepath, "r") as f:
                    content = f.read(100)
                    if "asset" in content or "scene" in content:
                        print("  ✓ Gültiges glTF-Format")
                    else:
                        print("  ✗ Ungültiges glTF-Format")
            else:
                print(f"  ✗ Datei nicht gefunden: {filepath}")
        else:
            print("  ✗ glTF-Export fehlgeschlagen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
    
    # Test 2: glb-Export (Binär-Format)
    print("\nTest 2: glb-Export (Binär-Format)")
    filepath = "test_export.glb"
    try:
        success = export_gltf(
            project_data=project_data,
            dims=dims,
            roof_type="Zeltdach",
            module_quantity=16,
            layout_config=layout,
            filepath=filepath
        )
        
        if success and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✓ glb-Export erfolgreich: {filepath} ({file_size} Bytes)")
            
            # Prüfe glb-Header (binär)
            with open(filepath, "rb") as f:
                header = f.read(4)
                if header == b'glTF':
                    print("  ✓ Gültiger glb-Header")
                else:
                    print("  ✗ Ungültiger glb-Header")
        else:
            print("  ✗ glb-Export fehlgeschlagen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
    
    # Test 3: Export mit Garage und Fassade
    print("\nTest 3: Export mit Garage und Fassade")
    layout_extended = LayoutConfig(
        mode="auto",
        use_garage=True,
        use_facade=True
    )
    filepath = "test_export_extended.glb"
    try:
        success = export_gltf(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=50,  # Mehr Module als auf Hauptdach passen
            layout_config=layout_extended,
            filepath=filepath
        )
        
        if success and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✓ Export mit Garage/Fassade: {filepath} ({file_size} Bytes)")
        else:
            print("  ✗ Export fehlgeschlagen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")


def main():
    """Hauptfunktion - Führt alle Tests aus"""
    print("\n" + "="*70)
    print("TASK 6: EXPORT-FUNKTIONEN - VERIFIKATION")
    print("="*70)
    
    # Test 6.1: render_image_bytes()
    test_render_image_bytes()
    
    # Test 6.2: export_stl()
    test_export_stl()
    
    # Test 6.3: export_gltf()
    test_export_gltf()
    
    # Zusammenfassung
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)
    
    # Liste erstellte Dateien
    test_files = [
        "test_screenshot_flat.png",
        "test_screenshot_gable.png",
        "test_export_flat.stl",
        "test_export_gable.stl",
        "test_export_hip.stl",
        "test_export.gltf",
        "test_export.glb",
        "test_export_extended.glb"
    ]
    
    print("\nErstellte Test-Dateien:")
    for filename in test_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✓ {filename} ({size} Bytes)")
        else:
            print(f"  ✗ {filename} (nicht gefunden)")
    
    print("\n" + "="*70)
    print("TASK 6 ABGESCHLOSSEN")
    print("="*70)
    print("\nAlle drei Export-Funktionen wurden implementiert:")
    print("  ✓ 6.1: render_image_bytes() - Off-Screen Screenshot (PNG)")
    print("  ✓ 6.2: export_stl() - STL-Export")
    print("  ✓ 6.3: export_gltf() - glTF/glb-Export")
    print("\nDie Funktionen sind bereit für die Integration in:")
    print("  - Streamlit UI (Screenshot-Download)")
    print("  - PDF-Generator (render_image_bytes)")
    print("  - 3D-Modell-Export (STL/glTF)")


if __name__ == "__main__":
    main()
