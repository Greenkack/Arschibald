"""
Test für Task 8.2: Modul-Details anzeigen

Testet ob Modul-Details (Nummer, Leistung, Azimut) korrekt im Hover-Text angezeigt werden.
"""

import sys
import os

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.pv3d_plotly import create_pv_module_3d


def test_module_details_hover():
    """
    Test 8.2: Modul-Details im Hover-Text
    
    Testet ob:
    - Modul-Nummer angezeigt wird
    - Leistung (W) angezeigt wird
    - Azimut (Grad und Himmelsrichtung) angezeigt wird
    - Neigung angezeigt wird
    - Position angezeigt wird
    """
    print("\n" + "=" * 70)
    print("TEST 8.2: MODUL-DETAILS IM HOVER-TEXT")
    print("=" * 70)
    
    # Test 1: Modul mit Nummer und Standard-Leistung (400W)
    print("\n📋 Test 1: Modul mit Nummer und Standard-Leistung")
    print("-" * 70)
    
    module_1, vertices_1 = create_pv_module_3d(
        x=0.0, y=0.0, z=5.0,
        azimuth_deg=0,  # Süd
        tilt_deg=30,
        module_number=1,
        module_power_w=400
    )
    
    # Prüfe ob hovertemplate vorhanden ist
    assert hasattr(module_1, 'hovertemplate'), "Modul hat kein hovertemplate"
    hover_text = module_1.hovertemplate
    
    # Prüfe ob alle Details enthalten sind
    assert "Modul #1" in hover_text, "Modul-Nummer fehlt im Hover-Text"
    assert "400 W" in hover_text, "Leistung fehlt im Hover-Text"
    assert "0.0°" in hover_text or "0.0° (Süd)" in hover_text, "Azimut fehlt im Hover-Text"
    assert "Süd" in hover_text, "Himmelsrichtung fehlt im Hover-Text"
    assert "30.0°" in hover_text, "Neigung fehlt im Hover-Text"
    assert "(0.00, 0.00, 5.00)" in hover_text, "Position fehlt im Hover-Text"
    
    print(f"Hover-Text enthält alle Details:")
    print(f"   {hover_text}")
    
    # Test 2: Modul mit höherer Leistung (450W) und West-Ausrichtung
    print("\n📋 Test 2: Modul mit 450W und West-Ausrichtung")
    print("-" * 70)
    
    module_2, vertices_2 = create_pv_module_3d(
        x=1.5, y=2.0, z=6.5,
        azimuth_deg=90,  # West
        tilt_deg=25,
        module_number=15,
        module_power_w=450
    )
    
    hover_text_2 = module_2.hovertemplate
    
    assert "Modul #15" in hover_text_2, "Modul-Nummer #15 fehlt"
    assert "450 W" in hover_text_2, "Leistung 450W fehlt"
    assert "90.0°" in hover_text_2, "Azimut 90° fehlt"
    assert "West" in hover_text_2, "Himmelsrichtung West fehlt"
    assert "25.0°" in hover_text_2, "Neigung 25° fehlt"
    
    print(f"Hover-Text für Modul #15 (450W, West):")
    print(f"   {hover_text_2}")
    
    # Test 3: Modul ohne Nummer
    print("\n📋 Test 3: Modul ohne Nummer")
    print("-" * 70)
    
    module_3, vertices_3 = create_pv_module_3d(
        x=0.0, y=0.0, z=5.0,
        azimuth_deg=180,  # Nord
        tilt_deg=35,
        module_number=None,  # Keine Nummer
        module_power_w=400
    )
    
    hover_text_3 = module_3.hovertemplate
    
    assert "PV Modul" in hover_text_3, "Generischer Name fehlt"
    assert "Modul #" not in hover_text_3, "Modul-Nummer sollte nicht vorhanden sein"
    assert "400 W" in hover_text_3, "Leistung fehlt"
    assert "180.0°" in hover_text_3, "Azimut fehlt"
    assert "Nord" in hover_text_3, "Himmelsrichtung Nord fehlt"
    
    print(f"Hover-Text ohne Modul-Nummer:")
    print(f"   {hover_text_3}")
    
    # Test 4: Verschiedene Himmelsrichtungen
    print("\n📋 Test 4: Verschiedene Himmelsrichtungen")
    print("-" * 70)
    
    directions = [
        (0, "Süd"),
        (45, "Süd-West"),
        (90, "West"),
        (135, "Nord-West"),
        (180, "Nord"),
        (225, "Nord-Ost"),
        (270, "Ost"),
        (315, "Süd-Ost"),
    ]
    
    for azimuth, expected_direction in directions:
        module, _ = create_pv_module_3d(
            x=0.0, y=0.0, z=5.0,
            azimuth_deg=azimuth,
            tilt_deg=30,
            module_number=1,
            module_power_w=400
        )
        
        hover_text = module.hovertemplate
        assert expected_direction in hover_text, \
            f"Himmelsrichtung '{expected_direction}' fehlt für Azimut {azimuth}°"
        print(f"   {azimuth:3d}° → {expected_direction}")
    
    print("\n" + "=" * 70)
    print("ALLE TESTS ERFOLGREICH!")
    print("=" * 70)
    print("\nTask 8.2 ist vollständig implementiert:")
    print("  Modul-Nummer wird im Hover-Text angezeigt")
    print("  Leistung (W) wird im Hover-Text angezeigt")
    print("  Azimut (Grad und Himmelsrichtung) wird angezeigt")
    print("  Neigung wird angezeigt")
    print("  Position wird angezeigt")
    print("  Himmelsrichtungen werden korrekt konvertiert")
    print("\n")


if __name__ == "__main__":
    try:
        test_module_details_hover()
    except AssertionError as e:
        print(f"\nTEST FEHLGESCHLAGEN: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNERWARTETER FEHLER: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
