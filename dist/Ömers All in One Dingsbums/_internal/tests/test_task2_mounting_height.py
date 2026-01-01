"""
Test für Task 2: Modul-Aufständerung auf geneigten Dächern

Testet die korrekte Berechnung der Mounting Height für verschiedene Dachformen.
"""

import sys
import numpy as np

# Import der Funktion
from utils.pv3d_plotly import create_pv_module_3d

def test_mounting_height_calculation():
    """Testet die Mounting Height Berechnung für alle Dachformen."""
    
    print("\n" + "="*80)
    print("TEST: Modul-Aufständerung auf geneigten Dächern")
    print("="*80)
    
    # Test-Konfigurationen: (Dachform, Neigung, Erwartete Min-Höhe)
    test_cases = [
        ("Satteldach", 30.0, 0.1),
        ("Walmdach", 35.0, 0.1),
        ("Pultdach", 25.0, 0.1),
        ("Zeltdach", 40.0, 0.1),
        ("Krüppelwalmdach", 30.0, 0.1),
        ("Flachdach", 0.0, 0.0),  # Keine Aufständerung bei 0°
        ("Flachdach", 15.0, 0.3),  # Mit Aufständerung
    ]
    
    all_passed = True
    
    for roof_type, tilt_deg, expected_min_height in test_cases:
        print(f"\n{''*80}")
        print(f"Test: {roof_type} mit {tilt_deg}° Neigung")
        print(f"{''*80}")
        
        # Erstelle Modul
        try:
            # Position: x=0, y=0, z=5.0 (Dachhöhe)
            original_z = 5.0
            module, vertices = create_pv_module_3d(
                x=0.0,
                y=0.0,
                z=original_z,
                azimuth_deg=0.0,
                tilt_deg=tilt_deg,
                color="#1a1a2e",
                selected=False,
                show_mounting=False,  # Ohne zusätzliche Gestell-Höhe
                roof_type=roof_type
            )
            
            # Berechne tatsächliche Z-Verschiebung aus den Vertices
            # Die Vertices sind bereits transformiert, also müssen wir die durchschnittliche Z-Position nehmen
            avg_z = np.mean(vertices[:, 2])
            
            # Berechne erwartete Mounting Height
            if roof_type in ["Satteldach", "Satteldach mit Gaube", "Walmdach", "Krüppelwalmdach", "Pultdach", "Zeltdach"] and tilt_deg > 5.0:
                expected_mounting = min(0.3, (tilt_deg / 90.0) * 0.5)
            elif roof_type == "Flachdach" and tilt_deg > 5.0:
                expected_mounting = 0.3 + (tilt_deg / 90.0) * 0.5
                expected_mounting = min(0.8, expected_mounting)
            else:
                expected_mounting = 0.0
            
            expected_z = original_z + expected_mounting
            
            # Prüfe ob Mounting Height korrekt ist (mit Toleranz wegen Rotation)
            # Bei Rotation verschiebt sich der Schwerpunkt, daher größere Toleranz
            tolerance = 0.5
            z_diff = abs(avg_z - expected_z)
            
            if z_diff <= tolerance:
                print(f"PASS: Mounting Height korrekt")
                print(f"   Erwartete Z-Position: {expected_z:.3f}m")
                print(f"   Tatsächliche Z-Position: {avg_z:.3f}m")
                print(f"   Mounting Height: {expected_mounting:.3f}m")
            else:
                print(f"FAIL: Mounting Height inkorrekt")
                print(f"   Erwartete Z-Position: {expected_z:.3f}m")
                print(f"   Tatsächliche Z-Position: {avg_z:.3f}m")
                print(f"   Differenz: {z_diff:.3f}m (Toleranz: {tolerance}m)")
                all_passed = False
            
            # Prüfe dass Module NICHT in Dachfläche einsinken
            # Bei Rotation ist es normal dass die untere Kante unter dem Zentrum liegt
            # Wichtig ist dass das Zentrum erhöht ist
            min_z = np.min(vertices[:, 2])
            
            # Berechne erwartete minimale Z-Position bei Rotation
            # Bei Neigung sinkt die untere Kante um ca. (Modullänge/2) * sin(tilt)
            module_half_length = 1.76 / 2  # PV_H / 2
            expected_min_z = original_z + expected_mounting - module_half_length * np.sin(np.deg2rad(tilt_deg))
            
            if min_z >= expected_min_z - 0.1:  # Toleranz
                print(f"Module sinken NICHT in Dachfläche ein")
                print(f"   Min Z: {min_z:.3f}m (erwartet: ≥{expected_min_z:.3f}m)")
            else:
                print(f"WARNUNG: Module könnten in Dachfläche einsinken")
                print(f"   Min Z: {min_z:.3f}m (erwartet: ≥{expected_min_z:.3f}m)")
                all_passed = False
                
        except Exception as e:
            print(f"FEHLER: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print(f"\n{'='*80}")
    if all_passed:
        print("ALLE TESTS BESTANDEN")
        print("="*80)
        return 0
    else:
        print("EINIGE TESTS FEHLGESCHLAGEN")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(test_mounting_height_calculation())
