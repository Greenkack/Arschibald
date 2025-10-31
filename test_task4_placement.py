"""
Test für Task 4: PV-Modul-Platzierungs-Algorithmen

Testet die Funktionen:
- grid_positions()
- place_panels_auto()
- place_panels_manual()
- place_panels_flat_roof()
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import (
    grid_positions,
    place_panels_auto,
    place_panels_manual,
    place_panels_flat_roof
)


def test_grid_positions():
    """Test grid_positions Funktion"""
    print("Test 1: grid_positions()")
    print("-" * 50)
    
    # Test 1: Normale Fläche
    positions = grid_positions(10.0, 6.0)
    print(f"  10m x 6m Fläche: {len(positions)} Positionen")
    assert len(positions) > 0, "Sollte Positionen zurückgeben"
    
    # Test 2: Zu kleine Fläche
    positions = grid_positions(0.5, 0.5)
    print(f"  0.5m x 0.5m Fläche: {len(positions)} Positionen")
    assert len(positions) == 0, "Sollte keine Positionen zurückgeben"
    
    # Test 3: Erste Position prüfen
    positions = grid_positions(10.0, 6.0)
    x, y = positions[0]
    print(f"  Erste Position: ({x:.2f}, {y:.2f})")
    
    print("  ✓ grid_positions() funktioniert\n")


def test_place_panels_auto():
    """Test place_panels_auto Funktion"""
    print("Test 2: place_panels_auto()")
    print("-" * 50)
    
    # Test 1: Flachdach
    panels = place_panels_auto(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=20,
        roof_type="Flachdach",
        inclination_deg=0.0,
        base_z=6.0
    )
    print(f"  Flachdach, 20 Module gewünscht: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte Module platzieren"
    assert len(panels) <= 20, "Sollte nicht mehr als gewünscht platzieren"
    
    # Test 2: Satteldach
    panels = place_panels_auto(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=15,
        roof_type="Satteldach",
        inclination_deg=35.0,
        base_z=6.0
    )
    print(f"  Satteldach 35°, 15 Module: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte Module platzieren"
    
    # Test 3: Mehr Module als Platz
    panels = place_panels_auto(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=1000,
        roof_type="Flachdach",
        base_z=6.0
    )
    print(f"  1000 Module gewünscht: {len(panels)} platziert (Kapazität)")
    assert len(panels) < 1000, "Sollte auf Kapazität begrenzen"
    
    print("  ✓ place_panels_auto() funktioniert\n")


def test_place_panels_manual():
    """Test place_panels_manual Funktion"""
    print("Test 3: place_panels_manual()")
    print("-" * 50)
    
    # Test 1: Ohne entfernte Module
    panels = place_panels_manual(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=20,
        removed_indices=[],
        roof_type="Flachdach",
        base_z=6.0
    )
    print(f"  20 Module, keine entfernt: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte Module platzieren"
    
    # Test 2: Mit entfernten Modulen
    panels = place_panels_manual(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=20,
        removed_indices=[0, 1, 2, 5, 10],
        roof_type="Flachdach",
        base_z=6.0
    )
    expected = 20 - 5  # 5 Module entfernt
    print(f"  20 Module, 5 entfernt: {len(panels)} platziert")
    # Kann weniger sein wenn nicht alle 20 passen
    assert len(panels) <= expected, "Sollte entfernte Module auslassen"
    
    # Test 3: Ungültige Indizes
    panels = place_panels_manual(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=10,
        removed_indices=[0, 1, 100, 200, -5],  # 100, 200, -5 ungültig
        roof_type="Flachdach",
        base_z=6.0
    )
    print(f"  10 Module, ungültige Indizes: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte ungültige Indizes ignorieren"
    
    print("  ✓ place_panels_manual() funktioniert\n")


def test_place_panels_flat_roof():
    """Test place_panels_flat_roof Funktion"""
    print("Test 4: place_panels_flat_roof()")
    print("-" * 50)
    
    # Test 1: Süd-Aufständerung
    panels = place_panels_flat_roof(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=20,
        mounting_type="south",
        base_z=6.0
    )
    print(f"  Süd-Aufständerung, 20 Module: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte Module platzieren"
    
    # Test 2: Ost-West-Aufständerung
    panels = place_panels_flat_roof(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=20,
        mounting_type="east-west",
        base_z=6.0
    )
    print(f"  Ost-West-Aufständerung, 20 Module: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte Module platzieren"
    # Ost-West hat weniger Kapazität wegen Reihenfilterung
    
    # Test 3: Mit entfernten Modulen
    panels = place_panels_flat_roof(
        roof_length=10.0,
        roof_width=6.0,
        module_quantity=15,
        mounting_type="south",
        removed_indices=[0, 1, 2],
        base_z=6.0
    )
    print(f"  Süd, 15 Module, 3 entfernt: {len(panels)} platziert")
    assert len(panels) > 0, "Sollte Module platzieren"
    
    print("  ✓ place_panels_flat_roof() funktioniert\n")


def main():
    """Führe alle Tests aus"""
    print("\n" + "=" * 50)
    print("Task 4: PV-Modul-Platzierungs-Algorithmen Tests")
    print("=" * 50 + "\n")
    
    try:
        test_grid_positions()
        test_place_panels_auto()
        test_place_panels_manual()
        test_place_panels_flat_roof()
        
        print("=" * 50)
        print("✓ Alle Tests erfolgreich!")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test fehlgeschlagen: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
