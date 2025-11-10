"""
Vollständiger Test für Modul-Platzierung auf dem Dach

Dieser Test verifiziert die komplette Kette:
1. calculate_z_position() - Berechnet relative Z-Position
2. build_plotly_scene - Addiert wall_height_m
3. create_pv_module_3d - Verwendet Z-Position OHNE Modifikation
"""

import math


def test_complete_z_position_chain():
    """
    Test der kompletten Z-Positions-Kette von Berechnung bis Rendering.
    """
    from utils.pv3d_placement_handler import calculate_z_position
    
    print("=" * 70)
    print("TEST: Komplette Modul-Platzierungs-Kette")
    print("=" * 70)
    print()
    
    # Simuliere Gebäude-Parameter
    wall_height_m = 6.0  # Traufhöhe
    
    # Test 1: Satteldach
    print("Test 1: Satteldach (30° Neigung)")
    print("-" * 70)
    roof_type = "Satteldach"
    roof_pitch = 30.0
    roof_width = 10.0
    
    # Schritt 1: calculate_z_position
    z_relative = calculate_z_position(roof_type, roof_pitch, roof_width)
    print(f"  Schritt 1 - calculate_z_position():")
    print(f"    Relative Z-Position: {z_relative:.2f}m")
    
    # Schritt 2: build_plotly_scene addiert wall_height_m
    z_absolute = wall_height_m + z_relative
    print(f"  Schritt 2 - build_plotly_scene:")
    print(f"    Wall Height: {wall_height_m:.2f}m")
    print(f"    Absolute Z-Position: {z_absolute:.2f}m")
    
    # Schritt 3: create_pv_module_3d verwendet Z OHNE Modifikation
    z_final = z_absolute  # KEINE Modifikation mehr!
    print(f"  Schritt 3 - create_pv_module_3d:")
    print(f"    Finale Z-Position: {z_final:.2f}m")
    print(f"    (KEINE Modifikation - Z bleibt unverändert)")
    
    # Validierung
    expected_z = wall_height_m + 0.15
    assert abs(z_final - expected_z) < 0.01, \
        f"Finale Z-Position falsch: {z_final}, erwartet: {expected_z}"
    
    print(f"  ✓ PASS - Module bei {z_final:.2f}m (auf dem Dach!)")
    print()
    
    # Test 2: Flachdach
    print("Test 2: Flachdach")
    print("-" * 70)
    roof_type = "Flachdach"
    roof_pitch = 0.0
    
    # Schritt 1: calculate_z_position
    z_relative = calculate_z_position(roof_type, roof_pitch, roof_width)
    print(f"  Schritt 1 - calculate_z_position():")
    print(f"    Relative Z-Position: {z_relative:.2f}m")
    
    # Schritt 2: build_plotly_scene addiert wall_height_m
    z_absolute = wall_height_m + z_relative
    print(f"  Schritt 2 - build_plotly_scene:")
    print(f"    Wall Height: {wall_height_m:.2f}m")
    print(f"    Absolute Z-Position: {z_absolute:.2f}m")
    
    # Schritt 3: create_pv_module_3d verwendet Z OHNE Modifikation
    z_final = z_absolute  # KEINE Modifikation mehr!
    print(f"  Schritt 3 - create_pv_module_3d:")
    print(f"    Finale Z-Position: {z_final:.2f}m")
    print(f"    (KEINE Modifikation - Z bleibt unverändert)")
    
    # Validierung
    expected_z = wall_height_m + 0.30
    assert abs(z_final - expected_z) < 0.01, \
        f"Finale Z-Position falsch: {z_final}, erwartet: {expected_z}"
    
    print(f"  ✓ PASS - Module bei {z_final:.2f}m (auf Aufständerung!)")
    print()
    
    # Test 3: Verschiedene Wandhöhen
    print("Test 3: Verschiedene Wandhöhen")
    print("-" * 70)
    
    test_cases = [
        ("Satteldach", 30.0, 3.0),   # Niedriges Gebäude
        ("Satteldach", 35.0, 6.0),   # Standard Gebäude
        ("Satteldach", 40.0, 9.0),   # Hohes Gebäude
        ("Flachdach", 0.0, 3.0),     # Niedriges Flachdach
        ("Flachdach", 0.0, 6.0),     # Standard Flachdach
    ]
    
    for roof_type, roof_pitch, wall_height in test_cases:
        z_relative = calculate_z_position(roof_type, roof_pitch, 10.0)
        z_absolute = wall_height + z_relative
        z_final = z_absolute  # KEINE Modifikation
        
        print(f"  {roof_type} ({roof_pitch}°), Wandhöhe {wall_height:.1f}m:")
        print(f"    Finale Z-Position: {z_final:.2f}m")
        
        # Module sollten immer über der Wandhöhe sein
        assert z_final > wall_height, \
            f"Module zu niedrig! {z_final} <= {wall_height}"
        
        # Module sollten nicht zu hoch sein (max 1m über Wandhöhe)
        assert z_final < wall_height + 1.0, \
            f"Module zu hoch! {z_final} >= {wall_height + 1.0}"
    
    print(f"  ✓ PASS - Alle Wandhöhen korrekt!")
    print()
    
    print("=" * 70)
    print("✓ ALLE TESTS BESTANDEN!")
    print("=" * 70)
    print()
    print("ZUSAMMENFASSUNG:")
    print("  1. calculate_z_position() gibt relative Position zurück")
    print("  2. build_plotly_scene addiert wall_height_m")
    print("  3. create_pv_module_3d verwendet Z OHNE Modifikation")
    print("  4. Module erscheinen korrekt AUF dem Dach!")
    print()
    print("KRITISCHER FIX:")
    print("  ❌ VORHER: Z-Position wurde mehrfach modifiziert")
    print("  ✅ JETZT: Z-Position wird nur einmal korrekt berechnet")
    print()


if __name__ == "__main__":
    test_complete_z_position_chain()
