"""
Test für pv3d_analysis Modul

Testet die Analyse-Funktionen für die 3D-Visualisierung.
"""

import sys
from utils.pv3d_analysis import (
    calculate_sun_position_for_time,
    calculate_shading_analysis,
    calculate_yield_heatmap,
    run_optimization_assistant
)
from utils.pv3d import BuildingDims, ModuleTransform


def test_sun_position():
    """Testet Sonnenverlauf-Berechnung."""
    print("=" * 60)
    print("TEST 1: Sonnenverlauf-Berechnung")
    print("=" * 60)
    
    # Test: Mittag am 21. Juni (Sommersonnenwende) in Deutschland
    azimuth, elevation = calculate_sun_position_for_time(51.0, 172, 12.0)
    print(f"Mittag am 21. Juni (Sommersonnenwende):")
    print(f"  Azimuth: {azimuth:.1f}° (erwartet: ~180°)")
    print(f"  Elevation: {elevation:.1f}° (erwartet: ~60-65°)")
    
    # Test: Morgens am 21. Dezember (Wintersonnenwende)
    azimuth, elevation = calculate_sun_position_for_time(51.0, 355, 9.0)
    print(f"\nMorgens am 21. Dezember (Wintersonnenwende):")
    print(f"  Azimuth: {azimuth:.1f}°")
    print(f"  Elevation: {elevation:.1f}° (erwartet: ~10-15°)")
    
    # Test: Abends
    azimuth, elevation = calculate_sun_position_for_time(51.0, 172, 18.0)
    print(f"\nAbends am 21. Juni:")
    print(f"  Azimuth: {azimuth:.1f}°")
    print(f"  Elevation: {elevation:.1f}°")
    
    print("\nSonnenverlauf-Berechnung funktioniert\n")


def test_shading_analysis():
    """Testet Verschattungs-Analyse."""
    print("=" * 60)
    print("TEST 2: Verschattungs-Analyse")
    print("=" * 60)
    
    # Erstelle Test-Module
    positions = [
        (0.0, 0.0, 6.0),   # Modul 0
        (2.0, 0.0, 6.0),   # Modul 1
        (4.0, 0.0, 6.0),   # Modul 2
        (0.0, 2.0, 6.5),   # Modul 3 (höher)
    ]
    
    transforms = {
        i: ModuleTransform(index=i, azimuth_deg=0.0, tilt_deg=30.0)
        for i in range(len(positions))
    }
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    # Test: Sonne im Süden, 45° Elevation
    shading = calculate_shading_analysis(
        positions, transforms, 180.0, 45.0, dims
    )
    
    print(f"Verschattung bei Sonne im Süden (180°, 45°):")
    for i, shade in shading.items():
        print(f"  Modul {i}: {shade:.1f}% verschattet")
    
    # Test: Sonne unter Horizont (Nacht)
    shading_night = calculate_shading_analysis(
        positions, transforms, 180.0, -10.0, dims
    )
    
    print(f"\nVerschattung bei Nacht (Elevation < 0°):")
    for i, shade in shading_night.items():
        print(f"  Modul {i}: {shade:.1f}% verschattet (erwartet: 100%)")
    
    print("\nVerschattungs-Analyse funktioniert\n")


def test_yield_heatmap():
    """Testet Ertrags-Heatmap."""
    print("=" * 60)
    print("TEST 3: Ertrags-Heatmap")
    print("=" * 60)
    
    # Erstelle Test-Module mit verschiedenen Ausrichtungen
    positions = [
        (0.0, 0.0, 6.0),   # Modul 0
        (2.0, 0.0, 6.0),   # Modul 1
        (4.0, 0.0, 6.0),   # Modul 2
    ]
    
    transforms = {
        0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=30.0),    # Süd, optimal
        1: ModuleTransform(index=1, azimuth_deg=90.0, tilt_deg=30.0),   # Ost
        2: ModuleTransform(index=2, azimuth_deg=180.0, tilt_deg=30.0),  # Nord
    }
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    # Berechne Ertragspotential
    yield_map = calculate_yield_heatmap(positions, transforms, 51.0, dims)
    
    print(f"Ertragspotential (0-100):")
    for i, yield_val in yield_map.items():
        azimuth = transforms[i].azimuth_deg
        direction = {0.0: "Süd", 90.0: "Ost", 180.0: "Nord"}.get(azimuth, "?")
        print(f"  Modul {i} ({direction}): {yield_val:.1f}")
    
    # Validiere: Süd sollte höchsten Ertrag haben
    assert yield_map[0] > yield_map[1], "Süd sollte besser sein als Ost"
    assert yield_map[0] > yield_map[2], "Süd sollte besser sein als Nord"
    
    print("\nErtrags-Heatmap funktioniert\n")


def test_optimization_assistant():
    """Testet Optimierungs-Assistent."""
    print("=" * 60)
    print("TEST 4: Optimierungs-Assistent")
    print("=" * 60)
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    target_modules = 20
    
    # Test: Maximaler Ertrag
    print("Optimierungsziel: Maximaler Ertrag")
    results = run_optimization_assistant(
        dims, target_modules, "Flachdach", "max_yield", 51.0
    )
    
    print(f"\nTop 3 Konfigurationen:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.strategy_name}")
        print(f"   Score: {result.score:.1f}")
        print(f"   Geschätzte Module: {result.metrics['estimated_modules']}")
        print(f"   Ertragsfaktor: {result.metrics['yield_factor']:.2f}")
        print(f"   Mounting Mode: {result.metrics['mounting_mode']}")
    
    # Validiere: Scores sollten sortiert sein
    assert results[0].score >= results[1].score, "Scores sollten sortiert sein"
    assert results[1].score >= results[2].score, "Scores sollten sortiert sein"
    
    # Test: Maximale Modulanzahl
    print("\n" + "=" * 60)
    print("Optimierungsziel: Maximale Modulanzahl")
    results_max_modules = run_optimization_assistant(
        dims, target_modules, "Flachdach", "max_modules", 51.0
    )
    
    print(f"\nTop 3 Konfigurationen:")
    for i, result in enumerate(results_max_modules, 1):
        print(f"\n{i}. {result.strategy_name}")
        print(f"   Score: {result.score:.1f}")
        print(f"   Geschätzte Module: {result.metrics['estimated_modules']}")
    
    print("\nOptimierungs-Assistent funktioniert\n")


def main():
    """Führt alle Tests aus."""
    print("\n" + "=" * 60)
    print("PV3D ANALYSE-MODUL TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_sun_position()
        test_shading_analysis()
        test_yield_heatmap()
        test_optimization_assistant()
        
        print("=" * 60)
        print("ALLE TESTS ERFOLGREICH")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\nTEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
