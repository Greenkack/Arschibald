"""
Debug-Script für Modul-Positionierung

Testet ob die Grid-Berechnung korrekte Positionen liefert.
"""

def test_grid_calculation():
    """Test Grid-Berechnung"""
    from utils.pv3d_grid_calculator import calculate_module_grid
    
    print("\n=== Test: Grid-Berechnung ===")
    
    # Test mit realistischen Werten (wie im Screenshot)
    roof_length = 12.0  # 12m
    roof_width = 10.0   # 10m
    module_quantity = 20
    
    print(f"\nParameter:")
    print(f"  Dachlänge: {roof_length}m")
    print(f"  Dachbreite: {roof_width}m")
    print(f"  Modulanzahl: {module_quantity}")
    
    positions = calculate_module_grid(
        roof_length=roof_length,
        roof_width=roof_width,
        module_quantity=module_quantity
    )
    
    print(f"\nErgebnis:")
    print(f"  Anzahl Positionen: {len(positions)}")
    
    if positions:
        print(f"\n  Erste 5 Positionen:")
        for i, (x, y) in enumerate(positions[:5]):
            print(f"    Modul {i+1}: x={x:.2f}m, y={y:.2f}m")
        
        # Prüfe ob alle Positionen unterschiedlich sind
        unique_positions = set(positions)
        if len(unique_positions) == len(positions):
            print(f"\n  Alle {len(positions)} Positionen sind unterschiedlich")
        else:
            print(f"\n  PROBLEM: Nur {len(unique_positions)} einzigartige Positionen von {len(positions)}")
            print(f"     Es gibt Duplikate!")
        
        # Prüfe Verteilung
        x_coords = [x for x, y in positions]
        y_coords = [y for x, y in positions]
        
        print(f"\n  X-Koordinaten:")
        print(f"    Min: {min(x_coords):.2f}m")
        print(f"    Max: {max(x_coords):.2f}m")
        print(f"    Spanne: {max(x_coords) - min(x_coords):.2f}m")
        
        print(f"\n  Y-Koordinaten:")
        print(f"    Min: {min(y_coords):.2f}m")
        print(f"    Max: {max(y_coords):.2f}m")
        print(f"    Spanne: {max(y_coords) - min(y_coords):.2f}m")
        
    else:
        print("  FEHLER: Keine Positionen berechnet!")
    
    return positions


def test_3d_conversion():
    """Test 2D zu 3D Konvertierung"""
    from utils.pv3d_placement_handler import calculate_z_position
    
    print("\n\n=== Test: 2D zu 3D Konvertierung ===")
    
    # Hole 2D Positionen
    positions_2d = test_grid_calculation()
    
    if not positions_2d:
        print("\nKeine 2D Positionen zum Konvertieren!")
        return
    
    # Berechne Z-Position für Satteldach
    roof_type = "Satteldach"
    roof_pitch = 35.0
    
    z_position = calculate_z_position(roof_type, roof_pitch)
    
    print(f"\nZ-Position für {roof_type}:")
    print(f"  Z: {z_position:.3f}m")
    
    # Konvertiere zu 3D
    positions_3d = [
        (float(x), float(y), float(z_position))
        for x, y in positions_2d
    ]
    
    print(f"\n3D Positionen (erste 5):")
    for i, (x, y, z) in enumerate(positions_3d[:5]):
        print(f"  Modul {i+1}: x={x:.2f}m, y={y:.2f}m, z={z:.3f}m")
    
    # Prüfe ob alle Z-Werte gleich sind (sollten sie sein)
    z_coords = [z for x, y, z in positions_3d]
    if len(set(z_coords)) == 1:
        print(f"\n  Alle Z-Koordinaten sind gleich ({z_coords[0]:.3f}m)")
    else:
        print(f"\n  Z-Koordinaten variieren: {set(z_coords)}")
    
    # Prüfe ob X und Y variieren
    x_coords = [x for x, y, z in positions_3d]
    y_coords = [y for x, y, z in positions_3d]
    
    if len(set(x_coords)) > 1 and len(set(y_coords)) > 1:
        print(f"  X und Y Koordinaten variieren korrekt")
    else:
        print(f"  PROBLEM: X oder Y Koordinaten variieren nicht!")
        print(f"     Einzigartige X-Werte: {len(set(x_coords))}")
        print(f"     Einzigartige Y-Werte: {len(set(y_coords))}")


if __name__ == "__main__":
    print("=" * 70)
    print("DEBUG: MODUL-POSITIONIERUNG")
    print("=" * 70)
    
    try:
        test_3d_conversion()
        
        print("\n" + "=" * 70)
        print("DEBUG ABGESCHLOSSEN")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nFEHLER: {e}")
        import traceback
        traceback.print_exc()
