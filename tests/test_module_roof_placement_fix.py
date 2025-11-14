"""
Test für Modul-Platzierung AUF dem Dach (nicht auf der Gebäudefläche)

Dieser Test verifiziert, dass Module korrekt auf der Dachoberfläche
platziert werden und nicht auf der Gebäudefläche (Boden).
"""

import math


def test_z_position_calculation():
    """
    Test der Z-Positions-Berechnung für verschiedene Dachtypen.
    """
    from utils.pv3d_placement_handler import calculate_z_position
    
    print("=" * 70)
    print("TEST: Modul-Platzierung AUF dem Dach")
    print("=" * 70)
    print()
    
    # Test 1: Flachdach
    print("Test 1: Flachdach")
    print("-" * 70)
    z_flat = calculate_z_position("Flachdach", 0.0, 10.0)
    print(f"  Dachtyp: Flachdach")
    print(f"  Z-Position: {z_flat:.2f}m")
    print(f"  Erwartung: 0.30m (Aufständerung)")
    assert abs(z_flat - 0.3) < 0.01, f"Flachdach Z-Position falsch: {z_flat}"
    print("  [OK] PASS")
    print()
    
    # Test 2: Satteldach mit 30° Neigung
    print("Test 2: Satteldach (30° Neigung, 10m Breite)")
    print("-" * 70)
    roof_width = 10.0
    roof_pitch = 30.0
    z_gable = calculate_z_position("Satteldach", roof_pitch, roof_width)
    
    # Erwartung: 0.15m über Traufhöhe (Dachbasis)
    expected_z = 0.15
    
    print(f"  Dachtyp: Satteldach")
    print(f"  Dachneigung: {roof_pitch}°")
    print(f"  Dachbreite: {roof_width}m")
    print(f"  Z-Position (relativ zu Traufhöhe): {z_gable:.2f}m")
    print(f"  Erwartung: {expected_z:.2f}m (15cm über Dachbasis)")
    print(f"  Hinweis: Die Dachneigung wird durch die Dachgeometrie selbst dargestellt")
    
    # Module sollten leicht über der Dachbasis sein
    assert abs(z_gable - expected_z) < 0.01, \
        f"Satteldach Z-Position falsch: {z_gable}, erwartet: {expected_z}"
    
    # Module sollten NICHT auf der Gebäudefläche sein (z=0)
    assert z_gable > 0.0, \
        f"Module zu niedrig! Z={z_gable:.2f}m - sollten über der Dachbasis sein!"
    
    print("  [OK] PASS - Module sind korrekt positioniert!")
    print()
    
    # Test 3: Pultdach mit 25° Neigung
    print("Test 3: Pultdach (25° Neigung, 8m Breite)")
    print("-" * 70)
    roof_width = 8.0
    roof_pitch = 25.0
    z_pent = calculate_z_position("Pultdach", roof_pitch, roof_width)
    
    expected_z = 0.15
    
    print(f"  Dachtyp: Pultdach")
    print(f"  Dachneigung: {roof_pitch}°")
    print(f"  Dachbreite: {roof_width}m")
    print(f"  Z-Position (relativ zu Traufhöhe): {z_pent:.2f}m")
    print(f"  Erwartung: {expected_z:.2f}m (15cm über Dachbasis)")
    
    assert abs(z_pent - expected_z) < 0.01, \
        f"Pultdach Z-Position falsch: {z_pent}, erwartet: {expected_z}"
    assert z_pent > 0.0, \
        f"Module zu niedrig! Z={z_pent:.2f}m - sollten über der Dachbasis sein!"
    
    print("  [OK] PASS - Module sind korrekt positioniert!")
    print()
    
    # Test 4: Walmdach mit 35° Neigung
    print("Test 4: Walmdach (35° Neigung, 12m Breite)")
    print("-" * 70)
    roof_width = 12.0
    roof_pitch = 35.0
    z_hip = calculate_z_position("Walmdach", roof_pitch, roof_width)
    
    expected_z = 0.15
    
    print(f"  Dachtyp: Walmdach")
    print(f"  Dachneigung: {roof_pitch}°")
    print(f"  Dachbreite: {roof_width}m")
    print(f"  Z-Position (relativ zu Traufhöhe): {z_hip:.2f}m")
    print(f"  Erwartung: {expected_z:.2f}m (15cm über Dachbasis)")
    
    assert abs(z_hip - expected_z) < 0.01, \
        f"Walmdach Z-Position falsch: {z_hip}, erwartet: {expected_z}"
    assert z_hip > 0.0, \
        f"Module zu niedrig! Z={z_hip:.2f}m - sollten über der Dachbasis sein!"
    
    print("  [OK] PASS - Module sind korrekt positioniert!")
    print()
    
    # Test 5: Vergleich vorher/nachher
    print("Test 5: Vergleich alte vs. neue Berechnung")
    print("-" * 70)
    roof_width = 10.0
    roof_pitch = 30.0
    
    # Alte Berechnung (60% der Firsthöhe - zu niedrig, auf Gebäudefläche)
    ridge_height = (roof_width / 2) * math.tan(math.radians(roof_pitch))
    old_z = ridge_height * 0.6 + 0.05
    
    # Neue Berechnung (15cm über Dachbasis - korrekt auf Dach)
    new_z = calculate_z_position("Satteldach", roof_pitch, roof_width)
    
    print(f"  Firsthöhe: {ridge_height:.2f}m")
    print(f"  Alte Z-Position: {old_z:.2f}m [ERROR] (auf Gebäudefläche)")
    print(f"  Neue Z-Position: {new_z:.2f}m [OK] (auf Dachoberfläche)")
    print(f"  Hinweis: Z-Position ist relativ zur Traufhöhe")
    print(f"  Die Dachneigung wird durch die Dachgeometrie dargestellt")
    
    assert new_z == 0.15, "Neue Position sollte 0.15m sein!"
    
    print("  [OK] PASS - Module werden jetzt korrekt AUF dem Dach platziert!")
    print()
    
    print("=" * 70)
    print("[OK] ALLE TESTS BESTANDEN!")
    print("=" * 70)
    print()
    print("ZUSAMMENFASSUNG:")
    print("  • Flachdach: Module auf Aufständerung (0.30m über Dachbasis)")
    print("  • Geneigte Dächer: Module auf Dachoberfläche (0.15m über Traufhöhe)")
    print("  • Z-Position ist relativ zur Traufhöhe (wall_height_m)")
    print("  • Die Dachneigung wird durch die Dachgeometrie selbst dargestellt")
    print("  • Fix erfolgreich: Module korrekt auf dem Dach platziert!")
    print()


if __name__ == "__main__":
    test_z_position_calculation()
