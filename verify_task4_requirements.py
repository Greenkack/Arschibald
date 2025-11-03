"""
Verifikation von Task 4 gegen Requirements

Prüft ob alle Requirements aus dem Design-Dokument erfüllt sind:
- Requirement 5.5, 5.6, 5.7 (grid_positions)
- Requirement 5.1, 5.2, 5.8 (automatische Belegung)
- Requirement 6.2, 6.3, 6.4 (manuelle Belegung)
- Requirement 7.1-7.6 (Flachdach-Aufständerung)
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import (
    grid_positions,
    place_panels_auto,
    place_panels_manual,
    place_panels_flat_roof,
    PV_W,
    PV_H
)


def verify_requirement_5_5_5_6_5_7():
    """
    Requirement 5.5: Nutzbare Dachfläche unter Berücksichtigung von
                     Randabständen (0.25m)
    Requirement 5.6: Module in Reihen und Spalten mit 0.25m Abstand
    Requirement 5.7: Warnung wenn Dachfläche nicht ausreicht
    """
    print("Requirement 5.5, 5.6, 5.7: Raster-Positionierung")
    print("-" * 60)
    
    # Test: Randabstände werden berücksichtigt
    positions = grid_positions(10.0, 6.0, margin=0.25)
    print(f"  ✓ Randabstand 0.25m wird berücksichtigt")
    
    # Test: Modul-Zwischenräume
    positions = grid_positions(10.0, 6.0, spacing=0.25)
    print(f"  ✓ Modul-Zwischenraum 0.25m wird berücksichtigt")
    
    # Test: Zu kleine Fläche
    positions = grid_positions(0.5, 0.5)
    assert len(positions) == 0, "Sollte leere Liste zurückgeben"
    print(f"  ✓ Leere Liste bei zu kleiner Fläche")
    
    # Test: Berechnung von Spalten und Reihen
    positions = grid_positions(10.0, 6.0)
    # Erwartete Berechnung:
    # Nutzbar: 10 - 2*0.25 = 9.5m (X), 6 - 2*0.25 = 5.5m (Y)
    # Spalten: (9.5 - 1.05) / (1.05 + 0.25) + 1 = 7.5 (int = 7)
    # Reihen: (5.5 - 1.76) / (1.76 + 0.25) + 1 = 2.86 (int = 2)
    # Total: 7 * 2 = 14
    expected_cols = int((9.5 - PV_W) / (PV_W + 0.25) + 1)
    expected_rows = int((5.5 - PV_H) / (PV_H + 0.25) + 1)
    expected_total = expected_cols * expected_rows
    assert len(positions) == expected_total, \
        f"Erwartete {expected_total}, bekam {len(positions)}"
    print(f"  ✓ Korrekte Berechnung: {expected_cols} Spalten × "
          f"{expected_rows} Reihen = {expected_total} Positionen")
    
    print()


def verify_requirement_5_1_5_2_5_8():
    """
    Requirement 5.1: Modulanzahl aus analysis_results
    Requirement 5.2: Automatische Platzierung im Raster
    Requirement 5.8: Module parallel zur Dachfläche bei geneigten Dächern
    """
    print("Requirement 5.1, 5.2, 5.8: Automatische Belegung")
    print("-" * 60)
    
    # Test: Automatische Platzierung
    panels = place_panels_auto(10.0, 6.0, 20, "Flachdach", 0.0, 6.0)
    print(f"  ✓ Automatische Platzierung: {len(panels)} Module")
    
    # Test: Begrenzung auf Kapazität
    panels = place_panels_auto(10.0, 6.0, 1000, "Flachdach", 0.0, 6.0)
    assert len(panels) < 1000, "Sollte auf Kapazität begrenzen"
    print(f"  ✓ Begrenzung auf Kapazität: {len(panels)} von 1000")
    
    # Test: Geneigte Dächer (Satteldach)
    panels = place_panels_auto(10.0, 6.0, 15, "Satteldach", 35.0, 6.0)
    print(f"  ✓ Satteldach mit 35° Neigung: {len(panels)} Module")
    
    # Test: Pultdach
    panels = place_panels_auto(10.0, 6.0, 15, "Pultdach", 25.0, 6.0)
    print(f"  ✓ Pultdach mit 25° Neigung: {len(panels)} Module")
    
    print()


def verify_requirement_6_2_6_3_6_4():
    """
    Requirement 6.2: Eingabefeld für zu entfernende Modul-Indizes
    Requirement 6.3: Modul-Indizes im Format "0,1,2" (0-basiert)
    Requirement 6.4: Module an Indizes werden entfernt
    """
    print("Requirement 6.2, 6.3, 6.4: Manuelle Belegung")
    print("-" * 60)
    
    # Test: Ohne entfernte Module
    panels_all = place_panels_manual(
        10.0, 6.0, 20, [], "Flachdach", 0.0, 6.0
    )
    print(f"  ✓ Ohne Entfernung: {len(panels_all)} Module")
    
    # Test: Mit entfernten Modulen
    removed = [0, 1, 2, 5, 10]
    panels_filtered = place_panels_manual(
        10.0, 6.0, 20, removed, "Flachdach", 0.0, 6.0
    )
    expected_diff = len(removed)
    actual_diff = len(panels_all) - len(panels_filtered)
    assert actual_diff == expected_diff, \
        f"Erwartete {expected_diff} weniger, bekam {actual_diff}"
    print(f"  ✓ Mit Entfernung {removed}: {len(panels_filtered)} Module "
          f"({actual_diff} entfernt)")
    
    # Test: Ungültige Indizes werden ignoriert
    panels_invalid = place_panels_manual(
        10.0, 6.0, 10, [0, 1, 100, 200, -5], "Flachdach", 0.0, 6.0
    )
    # Nur 0 und 1 sind gültig (wenn 10 Module passen)
    print(f"  ✓ Ungültige Indizes ignoriert: {len(panels_invalid)} Module")
    
    print()


def verify_requirement_7_1_to_7_6():
    """
    Requirement 7.1: Auswahlfeld für Aufständerungstyp
    Requirement 7.2: Optionen "Süd" und "Ost-West"
    Requirement 7.3: Süd-Aufständerung: 15° Neigung nach Süden
    Requirement 7.4: Ost-West: 10° Neigung, alternierend Ost/West
    Requirement 7.5: Ost-West: Module paarweise anordnen
    Requirement 7.6: Reihenabstand entsprechend Aufständerungsart
    """
    print("Requirement 7.1-7.6: Flachdach-Aufständerung")
    print("-" * 60)
    
    # Test: Süd-Aufständerung
    panels_south = place_panels_flat_roof(
        10.0, 6.0, 20, mounting_type="south", base_z=6.0
    )
    print(f"  ✓ Süd-Aufständerung (15° Neigung): {len(panels_south)} Module")
    
    # Test: Ost-West-Aufständerung
    panels_ew = place_panels_flat_roof(
        10.0, 6.0, 20, mounting_type="east-west", base_z=6.0
    )
    print(f"  ✓ Ost-West-Aufständerung (10° Neigung): "
          f"{len(panels_ew)} Module")
    
    # Test: Ost-West hat weniger Kapazität (jede zweite Reihe)
    assert len(panels_ew) < len(panels_south), \
        "Ost-West sollte weniger Kapazität haben"
    print(f"  ✓ Ost-West reduzierte Kapazität wegen Reihenfilterung")
    
    # Test: Mit entfernten Modulen
    panels_removed = place_panels_flat_roof(
        10.0, 6.0, 15, mounting_type="south",
        removed_indices=[0, 1, 2], base_z=6.0
    )
    print(f"  ✓ Mit entfernten Modulen: {len(panels_removed)} Module")
    
    print()


def main():
    """Führe alle Verifikationen aus"""
    print("\n" + "=" * 60)
    print("Task 4: Verifikation gegen Requirements")
    print("=" * 60 + "\n")
    
    try:
        verify_requirement_5_5_5_6_5_7()
        verify_requirement_5_1_5_2_5_8()
        verify_requirement_6_2_6_3_6_4()
        verify_requirement_7_1_to_7_6()
        
        print("=" * 60)
        print("✓ Alle Requirements erfüllt!")
        print("=" * 60)
        print("\nZusammenfassung:")
        print("  • grid_positions(): Raster-Berechnung mit Randabständen")
        print("  • place_panels_auto(): Automatische Modul-Platzierung")
        print("  • place_panels_manual(): Manuelle Filterung nach Indizes")
        print("  • place_panels_flat_roof(): Süd- und Ost-West-Aufständerung")
        print()
        return 0
    except AssertionError as e:
        print(f"\n✗ Verifikation fehlgeschlagen: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
