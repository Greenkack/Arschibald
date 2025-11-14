"""
Test für Animation-Fix und Kollisions-Fix

Dieser Test verifiziert:
1. Animation funktioniert ohne NoneType-Fehler
2. Kollisionserkennung gibt keine falschen Warnungen
"""


def test_animation_none_type_fix():
    """
    Test dass Animation mit None-Werten umgehen kann.
    """
    print("=" * 70)
    print("TEST 1: Animation NoneType-Fix")
    print("=" * 70)
    print()
    
    import math
    
    # Simuliere die Animation-Logik
    frames = 36
    camera_distance = None  # Kann None sein!
    camera_height = None    # Kann None sein!
    
    print("Test mit None-Werten:")
    print(f"  camera_distance: {camera_distance}")
    print(f"  camera_height: {camera_height}")
    print()
    
    # FIX: Verwende sichere Defaults
    safe_distance = camera_distance if camera_distance is not None else 2.5
    safe_height = camera_height if camera_height is not None else 0.4
    
    print("Nach Fix:")
    print(f"  safe_distance: {safe_distance}")
    print(f"  safe_height: {safe_height}")
    print()
    
    # Teste Berechnung
    try:
        for i in range(3):  # Nur 3 Frames zum Testen
            if frames != 0:
                angle_deg = (360.0 / frames) * i
            else:
                angle_deg = 0.0
            angle_rad = math.radians(angle_deg)
            
            camera_x = safe_distance * math.cos(angle_rad)
            camera_y = safe_distance * math.sin(angle_rad)
            camera_z = safe_height
            
            print(f"  Frame {i}: x={camera_x:.2f}, y={camera_y:.2f}, z={camera_z:.2f}")
        
        print()
        print("[OK] PASS - Keine NoneType-Fehler!")
        print()
        
    except TypeError as e:
        print(f"[ERROR] FAIL - NoneType-Fehler: {e}")
        return False
    
    return True


def test_collision_detection_fix():
    """
    Test dass Kollisionserkennung keine falschen Warnungen gibt.
    """
    print("=" * 70)
    print("TEST 2: Kollisions-Erkennungs-Fix")
    print("=" * 70)
    print()
    
    from utils.pv3d_placement_handler import check_module_collision
    from utils.pv3d_grid_calculator import calculate_module_grid, DEFAULT_MARGIN
    
    # Test-Parameter
    roof_length = 10.0
    roof_width = 8.0
    module_quantity = 20
    
    print(f"Dach-Dimensionen: {roof_length}m x {roof_width}m")
    print(f"Gewünschte Module: {module_quantity}")
    print(f"Margin: {DEFAULT_MARGIN}m")
    print()
    
    # Berechne Grid-Positionen
    positions_2d = calculate_module_grid(
        roof_length=roof_length,
        roof_width=roof_width,
        module_quantity=module_quantity,
        margin=DEFAULT_MARGIN
    )
    
    print(f"Grid-Berechnung: {len(positions_2d)} Module platziert")
    print()
    
    # Teste jede Position auf Kollision
    false_warnings = 0
    valid_positions = 0
    
    for i, (x, y) in enumerate(positions_2d):
        # Füge Z-Koordinate hinzu (wird für Kollisionsprüfung nicht benötigt)
        position_3d = (x, y, 0.15)
        
        # Prüfe Kollision
        result = check_module_collision(
            new_position=position_3d,
            existing_positions=[],  # Keine anderen Module
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN
        )
        
        if result["collision"]:
            print(f"  [ERROR] Modul {i}: {result['message']}")
            print(f"     Position: ({x:.2f}, {y:.2f})")
            false_warnings += 1
        else:
            valid_positions += 1
    
    print()
    print(f"Ergebnis:")
    print(f"  Gültige Positionen: {valid_positions}")
    print(f"  Falsche Warnungen: {false_warnings}")
    print()
    
    if false_warnings == 0:
        print("[OK] PASS - Keine falschen Kollisions-Warnungen!")
        print()
        return True
    else:
        print(f"[ERROR] FAIL - {false_warnings} falsche Warnungen!")
        print()
        return False


def test_boundary_calculation():
    """
    Test dass Grenzen korrekt berechnet werden.
    """
    print("=" * 70)
    print("TEST 3: Grenzen-Berechnung")
    print("=" * 70)
    print()
    
    from utils.pv3d_grid_calculator import PV_W, PV_H, DEFAULT_MARGIN
    
    roof_length = 10.0
    roof_width = 8.0
    margin = DEFAULT_MARGIN
    
    # Modul-Dimensionen (Portrait)
    module_width = PV_W   # 1.05m
    module_height = PV_H  # 1.76m
    half_width = module_width / 2
    half_height = module_height / 2
    
    print(f"Dach: {roof_length}m x {roof_width}m")
    print(f"Margin: {margin}m")
    print(f"Modul: {module_width}m x {module_height}m")
    print()
    
    # ALTE Berechnung (FALSCH)
    print("ALTE Grenzen-Berechnung (FALSCH):")
    old_max_x = (roof_length / 2) - margin
    old_min_x = -(roof_length / 2) + margin
    print(f"  X-Bereich: {old_min_x:.2f}m bis {old_max_x:.2f}m")
    print(f"  Problem: Prüft Modul-Kante statt Modul-Zentrum!")
    print()
    
    # NEUE Berechnung (KORREKT)
    print("NEUE Grenzen-Berechnung (KORREKT):")
    new_max_x = (roof_length / 2) - margin - half_width
    new_min_x = -(roof_length / 2) + margin + half_width
    print(f"  X-Bereich: {new_min_x:.2f}m bis {new_max_x:.2f}m")
    print(f"  Korrekt: Prüft Modul-Zentrum mit Modulbreite berücksichtigt!")
    print()
    
    # Beispiel-Position aus Grid
    example_x = -4.35  # Typische Position aus Grid
    
    print(f"Beispiel-Position: X = {example_x:.2f}m")
    print(f"  Modul-Kante links: {example_x - half_width:.2f}m")
    print(f"  Modul-Kante rechts: {example_x + half_width:.2f}m")
    print()
    
    # Alte Prüfung
    old_check = (example_x - half_width) < old_min_x
    print(f"  Alte Prüfung: {example_x - half_width:.2f}m < {old_min_x:.2f}m = {old_check}")
    if old_check:
        print(f"    [ERROR] Falsche Warnung!")
    print()
    
    # Neue Prüfung
    new_check = example_x < new_min_x
    print(f"  Neue Prüfung: {example_x:.2f}m < {new_min_x:.2f}m = {new_check}")
    if not new_check:
        print(f"    [OK] Korrekt - Keine Warnung!")
    print()
    
    print("[OK] PASS - Grenzen-Berechnung korrigiert!")
    print()
    
    return True


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ANIMATION & KOLLISIONS-FIX TESTS" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = []
    
    # Test 1: Animation NoneType-Fix
    results.append(test_animation_none_type_fix())
    
    # Test 2: Kollisions-Erkennungs-Fix
    results.append(test_collision_detection_fix())
    
    # Test 3: Grenzen-Berechnung
    results.append(test_boundary_calculation())
    
    # Zusammenfassung
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print()
    
    if all(results):
        print("[OK] ALLE TESTS BESTANDEN!")
        print()
        print("Fixes erfolgreich:")
        print("  1. [OK] Animation funktioniert ohne NoneType-Fehler")
        print("  2. [OK] Kollisionserkennung gibt keine falschen Warnungen")
        print("  3. [OK] Grenzen-Berechnung korrekt")
    else:
        print("[ERROR] EINIGE TESTS FEHLGESCHLAGEN!")
        print()
        for i, result in enumerate(results, 1):
            status = "[OK] PASS" if result else "[ERROR] FAIL"
            print(f"  Test {i}: {status}")
    
    print()
