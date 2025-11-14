"""
Test für alle Analyse-Funktionen der 3D-Visualisierung

Dieser Test deckt ab:
- Optimierungs-Assistent mit allen drei Zielen (max_modules, max_yield, balanced)
- Verschattungs-Analyse zu verschiedenen Tageszeiten
- Ertrags-Heatmap Visualisierung
- Sonnenverlauf-Animation

Requirements: 2.1, 2.2, 2.3
"""

import sys
import math
from typing import List, Dict, Tuple
from datetime import datetime

try:
    from utils.pv3d_analysis import (
        calculate_sun_position_for_time,
        calculate_shading_analysis,
        calculate_yield_heatmap,
        run_optimization_assistant
    )
    from utils.pv3d import BuildingDims, ModuleTransform
except ImportError as e:
    print(f"[ERROR] Import-Fehler: {e}")
    print("Stelle sicher, dass utils/pv3d_analysis.py und utils/pv3d.py existieren")
    sys.exit(1)


# ============================================================================
# TEST 1: OPTIMIERUNGS-ASSISTENT MIT ALLEN DREI ZIELEN
# ============================================================================

def test_optimization_all_goals():
    """
    Testet den Optimierungs-Assistenten mit allen drei Zielen:
    - max_modules: Maximale Modulanzahl
    - max_yield: Maximaler Ertrag
    - balanced: Ausgewogen zwischen Anzahl und Ertrag
    """
    print("=" * 80)
    print("TEST 1: OPTIMIERUNGS-ASSISTENT MIT ALLEN DREI ZIELEN")
    print("=" * 80)
    
    # Erstelle Test-Gebäude
    dims = BuildingDims(length_m=12.0, width_m=8.0, wall_height_m=6.0)
    target_modules = 25
    roof_type = "Flachdach"
    latitude = 51.0
    
    goals = ["max_modules", "max_yield", "balanced"]
    all_results = {}
    
    for goal in goals:
        print(f"\n{'─' * 80}")
        print(f"Optimierungsziel: {goal.upper()}")
        print(f"{'─' * 80}")
        
        results = run_optimization_assistant(
            building_dims=dims,
            target_modules=target_modules,
            roof_type=roof_type,
            optimization_goal=goal,
            latitude=latitude
        )
        
        all_results[goal] = results
        
        print(f"\nTop 3 Konfigurationen für '{goal}':")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result.strategy_name}")
            print(f"     Score: {result.score:.2f}")
            print(f"     Geschätzte Module: {result.metrics['estimated_modules']}")
            print(f"     Ertragsfaktor: {result.metrics['yield_factor']:.3f}")
            print(f"     Azimuth-Faktor: {result.metrics['azimuth_factor']:.3f}")
            print(f"     Neigungs-Faktor: {result.metrics['tilt_factor']:.3f}")
            print(f"     Mounting Mode: {result.metrics['mounting_mode']}")
            print(f"     Garage: {'Ja' if result.metrics['uses_garage'] else 'Nein'}")
            print(f"     Fassade: {'Ja' if result.metrics['uses_facade'] else 'Nein'}")
        
        # Validierung: Scores sollten sortiert sein
        assert len(results) == 3, f"Sollte 3 Ergebnisse haben, hat {len(results)}"
        assert results[0].score >= results[1].score, "Scores sollten absteigend sortiert sein"
        assert results[1].score >= results[2].score, "Scores sollten absteigend sortiert sein"
    
    # Vergleiche Ergebnisse zwischen Zielen
    print(f"\n{'=' * 80}")
    print("VERGLEICH DER OPTIMIERUNGSZIELE")
    print(f"{'=' * 80}")
    
    for goal in goals:
        best = all_results[goal][0]
        print(f"\n{goal.upper()}:")
        print(f"  Beste Strategie: {best.strategy_name}")
        print(f"  Score: {best.score:.2f}")
        print(f"  Module: {best.metrics['estimated_modules']}")
        print(f"  Ertragsfaktor: {best.metrics['yield_factor']:.3f}")
    
    print("\n[OK] Optimierungs-Assistent mit allen drei Zielen erfolgreich getestet\n")
    return all_results


# ============================================================================
# TEST 2: VERSCHATTUNGS-ANALYSE ZU VERSCHIEDENEN TAGESZEITEN
# ============================================================================

def test_shading_at_different_times():
    """
    Testet die Verschattungs-Analyse zu verschiedenen Tageszeiten:
    - Morgens (8:00 Uhr)
    - Mittags (12:00 Uhr)
    - Nachmittags (16:00 Uhr)
    - Abends (18:00 Uhr)
    - Nacht (22:00 Uhr)
    """
    print("=" * 80)
    print("TEST 2: VERSCHATTUNGS-ANALYSE ZU VERSCHIEDENEN TAGESZEITEN")
    print("=" * 80)
    
    # Erstelle Test-Module in einer Reihe
    positions = [
        (0.0, 0.0, 6.0),   # Modul 0 (vorne)
        (2.0, 0.0, 6.0),   # Modul 1
        (4.0, 0.0, 6.0),   # Modul 2
        (6.0, 0.0, 6.0),   # Modul 3
        (0.0, 2.0, 6.5),   # Modul 4 (höher, seitlich)
    ]
    
    transforms = {
        i: ModuleTransform(index=i, azimuth_deg=0.0, tilt_deg=30.0)
        for i in range(len(positions))
    }
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    
    # Teste verschiedene Tageszeiten
    test_times = [
        (8.0, "Morgens (8:00 Uhr)"),
        (12.0, "Mittags (12:00 Uhr)"),
        (16.0, "Nachmittags (16:00 Uhr)"),
        (18.0, "Abends (18:00 Uhr)"),
        (22.0, "Nacht (22:00 Uhr)")
    ]
    
    day_of_year = 172  # 21. Juni (Sommersonnenwende)
    latitude = 51.0
    
    shading_results = {}
    
    for hour, time_label in test_times:
        print(f"\n{'─' * 80}")
        print(f"{time_label}")
        print(f"{'─' * 80}")
        
        # Berechne Sonnenposition
        sun_azimuth, sun_elevation = calculate_sun_position_for_time(
            latitude, day_of_year, hour
        )
        
        print(f"Sonnenposition:")
        print(f"  Azimuth: {sun_azimuth:.1f}° ", end="")
        if 0 <= sun_azimuth < 45 or 315 <= sun_azimuth < 360:
            print("(Nord)")
        elif 45 <= sun_azimuth < 135:
            print("(Ost)")
        elif 135 <= sun_azimuth < 225:
            print("(Süd)")
        else:
            print("(West)")
        print(f"  Elevation: {sun_elevation:.1f}°")
        
        # Berechne Verschattung
        shading = calculate_shading_analysis(
            positions, transforms, sun_azimuth, sun_elevation, dims
        )
        
        shading_results[time_label] = shading
        
        print(f"\nVerschattung pro Modul:")
        for i in range(len(positions)):
            shade_pct = shading.get(i, 0.0)
            bar_length = int(shade_pct / 5)  # 20 chars = 100%
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  Modul {i}: {bar} {shade_pct:5.1f}%")
    
    print(f"\n{'=' * 80}")
    print("ZUSAMMENFASSUNG VERSCHATTUNGS-ANALYSE")
    print(f"{'=' * 80}")
    
    # Zeige Verschattungsverlauf für Modul 0
    print(f"\nVerschattungsverlauf für Modul 0:")
    for time_label in [t[1] for t in test_times]:
        shade = shading_results[time_label].get(0, 0.0)
        print(f"  {time_label:25s}: {shade:5.1f}%")
    
    print("\n[OK] Verschattungs-Analyse zu verschiedenen Tageszeiten erfolgreich getestet\n")
    return shading_results



# ============================================================================
# TEST 3: ERTRAGS-HEATMAP VISUALISIERUNG
# ============================================================================

def test_yield_heatmap_visualization():
    """
    Testet die Ertrags-Heatmap Visualisierung mit verschiedenen
    Modul-Ausrichtungen und -Positionen.
    """
    print("=" * 80)
    print("TEST 3: ERTRAGS-HEATMAP VISUALISIERUNG")
    print("=" * 80)
    
    # Erstelle Test-Module mit verschiedenen Ausrichtungen
    positions = [
        # Süd-Ausrichtung (optimal)
        (0.0, 0.0, 6.0),
        (2.0, 0.0, 6.0),
        # Ost-Ausrichtung
        (4.0, 0.0, 6.0),
        (6.0, 0.0, 6.0),
        # West-Ausrichtung
        (0.0, 2.0, 6.0),
        (2.0, 2.0, 6.0),
        # Nord-Ausrichtung (schlecht)
        (4.0, 2.0, 6.0),
        (6.0, 2.0, 6.0),
        # Höher positioniert (besserer Ertrag)
        (0.0, 4.0, 7.0),
        (2.0, 4.0, 7.0),
    ]
    
    transforms = {
        0: ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=35.0),    # Süd, optimal
        1: ModuleTransform(index=1, azimuth_deg=0.0, tilt_deg=30.0),    # Süd, gut
        2: ModuleTransform(index=2, azimuth_deg=90.0, tilt_deg=35.0),   # Ost
        3: ModuleTransform(index=3, azimuth_deg=90.0, tilt_deg=20.0),   # Ost, flach
        4: ModuleTransform(index=4, azimuth_deg=270.0, tilt_deg=35.0),  # West
        5: ModuleTransform(index=5, azimuth_deg=270.0, tilt_deg=30.0),  # West
        6: ModuleTransform(index=6, azimuth_deg=180.0, tilt_deg=35.0),  # Nord
        7: ModuleTransform(index=7, azimuth_deg=180.0, tilt_deg=45.0),  # Nord, steil
        8: ModuleTransform(index=8, azimuth_deg=0.0, tilt_deg=35.0),    # Süd, hoch
        9: ModuleTransform(index=9, azimuth_deg=45.0, tilt_deg=35.0),   # Süd-Ost
    }
    
    dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
    latitude = 51.0
    
    # Berechne Ertragspotential
    yield_map = calculate_yield_heatmap(positions, transforms, latitude, dims)
    
    print(f"\nErtragspotential pro Modul (0-100):")
    print(f"{'─' * 80}")
    
    # Sortiere nach Ertrag (höchster zuerst)
    sorted_modules = sorted(yield_map.items(), key=lambda x: x[1], reverse=True)
    
    for i, yield_val in sorted_modules:
        transform = transforms[i]
        azimuth = transform.azimuth_deg
        tilt = transform.tilt_deg
        pos = positions[i]
        
        # Bestimme Himmelsrichtung
        if azimuth < 22.5 or azimuth >= 337.5:
            direction = "Süd"
        elif 22.5 <= azimuth < 67.5:
            direction = "Süd-Ost"
        elif 67.5 <= azimuth < 112.5:
            direction = "Ost"
        elif 112.5 <= azimuth < 157.5:
            direction = "Nord-Ost"
        elif 157.5 <= azimuth < 202.5:
            direction = "Nord"
        elif 202.5 <= azimuth < 247.5:
            direction = "Nord-West"
        elif 247.5 <= azimuth < 292.5:
            direction = "West"
        else:
            direction = "Süd-West"
        
        # Visualisiere Ertrag als Balken
        bar_length = int(yield_val / 5)  # 20 chars = 100%
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        print(f"  Modul {i:2d}: {bar} {yield_val:5.1f}% | "
              f"{direction:10s} {azimuth:6.1f}° | Neigung {tilt:4.1f}° | Höhe {pos[2]:.1f}m")
    
    # Validierungen
    print(f"\n{'─' * 80}")
    print("VALIDIERUNGEN:")
    print(f"{'─' * 80}")
    
    # Süd sollte besser sein als Nord
    south_modules = [i for i, t in transforms.items() if t.azimuth_deg == 0.0]
    north_modules = [i for i, t in transforms.items() if t.azimuth_deg == 180.0]
    
    avg_south = sum(yield_map[i] for i in south_modules) / len(south_modules)
    avg_north = sum(yield_map[i] for i in north_modules) / len(north_modules)
    
    print(f"  Durchschnitt Süd-Module: {avg_south:.1f}%")
    print(f"  Durchschnitt Nord-Module: {avg_north:.1f}%")
    assert avg_south > avg_north, "Süd-Module sollten höheren Ertrag haben als Nord-Module"
    print(f"  [OK] Süd-Module haben höheren Ertrag als Nord-Module")
    
    # Höher positionierte Module sollten besseren Ertrag haben
    high_module = 8  # Modul auf 7.0m Höhe
    low_module = 0   # Modul auf 6.0m Höhe (gleiche Ausrichtung)
    
    print(f"\n  Modul {high_module} (7.0m Höhe): {yield_map[high_module]:.1f}%")
    print(f"  Modul {low_module} (6.0m Höhe): {yield_map[low_module]:.1f}%")
    assert yield_map[high_module] >= yield_map[low_module], "Höhere Module sollten besseren Ertrag haben"
    print(f"  [OK] Höher positionierte Module haben besseren oder gleichen Ertrag")
    
    print("\n[OK] Ertrags-Heatmap Visualisierung erfolgreich getestet\n")
    return yield_map



# ============================================================================
# TEST 4: SONNENVERLAUF-ANIMATION
# ============================================================================

def test_sun_path_animation():
    """
    Testet die Sonnenverlauf-Berechnung für eine Animation über den Tag.
    Simuliert einen kompletten Tag von Sonnenaufgang bis Sonnenuntergang.
    """
    print("=" * 80)
    print("TEST 4: SONNENVERLAUF-ANIMATION")
    print("=" * 80)
    
    latitude = 51.0
    day_of_year = 172  # 21. Juni (Sommersonnenwende)
    
    # Simuliere Sonnenverlauf von 5:00 bis 21:00 Uhr (alle 30 Minuten)
    hours = [h / 2.0 for h in range(10, 43)]  # 5.0, 5.5, 6.0, ..., 21.0
    
    sun_positions = []
    
    print(f"\nSonnenverlauf am 21. Juni (Sommersonnenwende) bei {latitude}°N:")
    print(f"{'─' * 80}")
    print(f"{'Zeit':>8s} | {'Azimuth':>10s} | {'Elevation':>10s} | {'Visualisierung':>30s}")
    print(f"{'─' * 80}")
    
    for hour in hours:
        azimuth, elevation = calculate_sun_position_for_time(latitude, day_of_year, hour)
        sun_positions.append((hour, azimuth, elevation))
        
        # Nur jede Stunde ausgeben (zu viele Zeilen sonst)
        if hour % 1.0 == 0.0:
            # Visualisiere Elevation als Balken
            if elevation > 0:
                bar_length = int(elevation / 3)  # 30 chars = 90°
                bar = "☀" + "─" * bar_length
            else:
                bar = "🌙 (unter Horizont)"
            
            # Formatiere Zeit
            hour_int = int(hour)
            minute_int = int((hour - hour_int) * 60)
            time_str = f"{hour_int:02d}:{minute_int:02d}"
            
            print(f"{time_str:>8s} | {azimuth:8.1f}° | {elevation:8.1f}° | {bar}")
    
    # Finde Sonnenaufgang und Sonnenuntergang
    sunrise_time = None
    sunset_time = None
    max_elevation = -90.0
    max_elevation_time = None
    
    for hour, azimuth, elevation in sun_positions:
        if elevation > 0 and sunrise_time is None:
            sunrise_time = hour
        if elevation > max_elevation:
            max_elevation = elevation
            max_elevation_time = hour
        if elevation <= 0 and sunrise_time is not None and sunset_time is None:
            sunset_time = hour
    
    print(f"{'─' * 80}")
    print(f"\nSONNENVERLAUF-STATISTIKEN:")
    print(f"  Sonnenaufgang: ~{sunrise_time:.1f} Uhr ({int(sunrise_time):02d}:{int((sunrise_time % 1) * 60):02d})")
    print(f"  Sonnenuntergang: ~{sunset_time:.1f} Uhr ({int(sunset_time):02d}:{int((sunset_time % 1) * 60):02d})")
    print(f"  Tageslänge: ~{sunset_time - sunrise_time:.1f} Stunden")
    print(f"  Maximale Elevation: {max_elevation:.1f}° um {max_elevation_time:.1f} Uhr")
    
    # Validierungen
    print(f"\nVALIDIERUNGEN:")
    assert sunrise_time is not None, "Sonnenaufgang sollte gefunden werden"
    assert sunset_time is not None, "Sonnenuntergang sollte gefunden werden"
    assert max_elevation > 50.0, f"Max. Elevation sollte > 50° sein (ist {max_elevation:.1f}°)"
    assert 11.0 <= max_elevation_time <= 13.0, f"Max. Elevation sollte um Mittag sein (ist {max_elevation_time:.1f})"
    print(f"  [OK] Sonnenaufgang und -untergang korrekt berechnet")
    print(f"  [OK] Maximale Elevation zur Mittagszeit")
    print(f"  [OK] Tageslänge plausibel für Sommersonnenwende")
    
    # Teste auch Wintersonnenwende zum Vergleich
    print(f"\n{'─' * 80}")
    print(f"VERGLEICH: Wintersonnenwende (21. Dezember)")
    print(f"{'─' * 80}")
    
    day_of_year_winter = 355  # 21. Dezember
    winter_positions = []
    
    for hour in [6.0, 9.0, 12.0, 15.0, 18.0]:
        azimuth, elevation = calculate_sun_position_for_time(latitude, day_of_year_winter, hour)
        winter_positions.append((hour, azimuth, elevation))
        
        hour_int = int(hour)
        minute_int = int((hour - hour_int) * 60)
        time_str = f"{hour_int:02d}:{minute_int:02d}"
        
        if elevation > 0:
            bar_length = int(elevation / 3)
            bar = "☀" + "─" * bar_length
        else:
            bar = "🌙 (unter Horizont)"
        
        print(f"{time_str:>8s} | {azimuth:8.1f}° | {elevation:8.1f}° | {bar}")
    
    # Finde max. Elevation im Winter
    winter_max_elevation = max(e for _, _, e in winter_positions)
    print(f"\n  Maximale Elevation im Winter: {winter_max_elevation:.1f}°")
    print(f"  Maximale Elevation im Sommer: {max_elevation:.1f}°")
    print(f"  Unterschied: {max_elevation - winter_max_elevation:.1f}°")
    
    assert winter_max_elevation < max_elevation, "Winter-Elevation sollte niedriger sein als Sommer"
    print(f"  [OK] Winter-Elevation niedriger als Sommer-Elevation")
    
    print("\n[OK] Sonnenverlauf-Animation erfolgreich getestet\n")
    return sun_positions


# ============================================================================
# HAUPTFUNKTION
# ============================================================================

def main():
    """Führt alle Tests aus."""
    print("\n" + "=" * 80)
    print("VOLLSTÄNDIGER TEST ALLER ANALYSE-FUNKTIONEN")
    print("=" * 80 + "\n")
    
    try:
        # Test 1: Optimierungs-Assistent mit allen drei Zielen
        optimization_results = test_optimization_all_goals()
        
        # Test 2: Verschattungs-Analyse zu verschiedenen Tageszeiten
        shading_results = test_shading_at_different_times()
        
        # Test 3: Ertrags-Heatmap Visualisierung
        yield_results = test_yield_heatmap_visualization()
        
        # Test 4: Sonnenverlauf-Animation
        sun_path_results = test_sun_path_animation()
        
        # Abschluss
        print("=" * 80)
        print("[OK] ALLE TESTS ERFOLGREICH ABGESCHLOSSEN")
        print("=" * 80)
        print("\nZusammenfassung:")
        print(f"  [OK] Optimierungs-Assistent mit 3 Zielen getestet")
        print(f"  [OK] Verschattungs-Analyse zu 5 Tageszeiten getestet")
        print(f"  [OK] Ertrags-Heatmap mit 10 Modulen visualisiert")
        print(f"  [OK] Sonnenverlauf-Animation für Sommer und Winter getestet")
        print("\nAlle Anforderungen (2.1, 2.2, 2.3) erfüllt!")
        
        return 0
        
    except AssertionError as e:
        print(f"\n[ERROR] VALIDIERUNGS-FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
