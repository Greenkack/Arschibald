"""
Test für 360° Animation Export

Testet die export_360_animation() Funktion aus utils/pv3d.py
"""

import os
import sys
import tempfile

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from pv3d import (
    BuildingDims,
    LayoutConfig,
    export_360_animation
)


def test_360_animation_basic():
    """Test: Grundlegende 360° Animation mit wenigen Frames"""
    print("\n" + "="*70)
    print("TEST: Grundlegende 360° Animation")
    print("="*70)
    
    # Erstelle BuildingDims
    dims = BuildingDims(
        length_m=10.0,
        width_m=6.0,
        wall_height_m=6.0
    )
    
    # Erstelle LayoutConfig
    layout = LayoutConfig(mode="auto")
    
    # Projekt-Daten
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 35.0,
            "roof_covering_type": "Ziegel"
        }
    }
    
    # Erstelle temporäre Datei
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.gif', delete=False) as tmp_file:
        tmp_filepath = tmp_file.name
    
    try:
        # Exportiere Animation mit nur 12 Frames für schnellen Test
        print(f"\nErstelle Animation mit 12 Frames...")
        gif_bytes = export_360_animation(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=15,
            layout_config=layout,
            filepath=tmp_filepath,
            frames=12,  # Wenige Frames für schnellen Test
            resolution=(400, 300),  # Kleine Auflösung für schnellen Test
            duration_ms=100
        )
        
        # Prüfe ob GIF-Bytes erstellt wurden
        assert gif_bytes, "GIF-Bytes sollten nicht leer sein"
        assert len(gif_bytes) > 0, "GIF-Bytes sollten Inhalt haben"
        
        # Prüfe ob Datei existiert
        assert os.path.exists(tmp_filepath), f"GIF-Datei sollte existieren: {tmp_filepath}"
        
        # Prüfe Dateigröße
        file_size = os.path.getsize(tmp_filepath)
        print(f"[OK] GIF erstellt: {file_size} Bytes")
        assert file_size > 1000, "GIF-Datei sollte mindestens 1KB groß sein"
        
        # Prüfe GIF-Header (GIF89a oder GIF87a)
        with open(tmp_filepath, 'rb') as f:
            header = f.read(6)
            assert header.startswith(b'GIF'), "Datei sollte ein gültiges GIF sein"
            print(f"[OK] GIF-Header: {header.decode('ascii', errors='ignore')}")
        
        print("\n[OK] Test erfolgreich: 360° Animation wurde erstellt")
        
    finally:
        # Lösche temporäre Datei
        if os.path.exists(tmp_filepath):
            os.unlink(tmp_filepath)
            print(f"[OK] Temporäre Datei gelöscht")


def test_360_animation_different_frames():
    """Test: Animation mit verschiedenen Frame-Anzahlen"""
    print("\n" + "="*70)
    print("TEST: Animation mit verschiedenen Frame-Anzahlen")
    print("="*70)
    
    dims = BuildingDims(length_m=8.0, width_m=5.0, wall_height_m=5.0)
    layout = LayoutConfig(mode="auto")
    project_data = {
        "project_details": {
            "roof_type": "Flachdach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 0.0,
            "roof_covering_type": "Bitumen"
        }
    }
    
    # Teste mit 18 Frames (20° pro Frame)
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.gif', delete=False) as tmp_file:
        tmp_filepath = tmp_file.name
    
    try:
        print(f"\nErstelle Animation mit 18 Frames...")
        gif_bytes = export_360_animation(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=10,
            layout_config=layout,
            filepath=tmp_filepath,
            frames=18,
            resolution=(400, 300),
            duration_ms=150
        )
        
        assert gif_bytes and len(gif_bytes) > 0, "GIF sollte erstellt werden"
        file_size = os.path.getsize(tmp_filepath)
        print(f"[OK] GIF mit 18 Frames erstellt: {file_size} Bytes")
        
        print("\n[OK] Test erfolgreich: Verschiedene Frame-Anzahlen funktionieren")
        
    finally:
        if os.path.exists(tmp_filepath):
            os.unlink(tmp_filepath)


def test_360_animation_with_modules():
    """Test: Animation mit PV-Modulen"""
    print("\n" + "="*70)
    print("TEST: Animation mit PV-Modulen")
    print("="*70)
    
    dims = BuildingDims(length_m=12.0, width_m=8.0, wall_height_m=6.0)
    layout = LayoutConfig(mode="auto", use_garage=False, use_facade=False)
    project_data = {
        "project_details": {
            "roof_type": "Satteldach",
            "roof_orientation": "Süd",
            "roof_inclination_deg": 30.0,
            "roof_covering_type": "Ziegel"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.gif', delete=False) as tmp_file:
        tmp_filepath = tmp_file.name
    
    try:
        print(f"\nErstelle Animation mit 20 PV-Modulen...")
        gif_bytes = export_360_animation(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            layout_config=layout,
            filepath=tmp_filepath,
            frames=12,
            resolution=(600, 400),
            duration_ms=100
        )
        
        assert gif_bytes and len(gif_bytes) > 0, "GIF mit Modulen sollte erstellt werden"
        file_size = os.path.getsize(tmp_filepath)
        print(f"[OK] GIF mit PV-Modulen erstellt: {file_size} Bytes")
        
        print("\n[OK] Test erfolgreich: Animation mit PV-Modulen funktioniert")
        
    finally:
        if os.path.exists(tmp_filepath):
            os.unlink(tmp_filepath)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("360° ANIMATION EXPORT TESTS")
    print("="*70)
    
    try:
        # Test 1: Grundlegende Animation
        test_360_animation_basic()
        
        # Test 2: Verschiedene Frame-Anzahlen
        test_360_animation_different_frames()
        
        # Test 3: Animation mit Modulen
        test_360_animation_with_modules()
        
        print("\n" + "="*70)
        print("[OK] ALLE TESTS ERFOLGREICH")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
