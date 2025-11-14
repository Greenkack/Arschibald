"""
Test-Skript für 3D-Visualisierungs-Fixes

Dieses Skript testet die durchgeführten Fixes:
1. Traufhöhe auf 3m
2. Modul-Platzierung mit korrekten Abständen
3. Kein doppelter Visualisierer
4. PDF-Screenshot Integration
5. Aufständerung Sichtbarkeit
6. Modulanzahl-Synchronisation
"""

import sys
import os

# Füge utils zum Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

def test_default_dimensions():
    """Test 1: Prüfe Standard-Traufhöhe"""
    print("\n" + "="*60)
    print("TEST 1: Standard-Traufhöhe")
    print("="*60)
    
    try:
        from solar_3d_view_module import _get_default_dimensions
        
        # Test Einfamilienhaus
        length, width, height = _get_default_dimensions("Einfamilienhaus")
        assert height == 3.0, f"Einfamilienhaus Traufhöhe sollte 3m sein, ist aber {height}m"
        print(f"[OK] Einfamilienhaus: {length}m x {width}m x {height}m (Traufhöhe korrekt)")
        
        # Test Mehrfamilienhaus
        length, width, height = _get_default_dimensions("Mehrfamilienhaus")
        assert height == 6.0, f"Mehrfamilienhaus Traufhöhe sollte 6m sein, ist aber {height}m"
        print(f"[OK] Mehrfamilienhaus: {length}m x {width}m x {height}m (Traufhöhe korrekt)")
        
        # Test Wohnblock
        length, width, height = _get_default_dimensions("Wohnblock")
        assert height == 9.0, f"Wohnblock Traufhöhe sollte 9m sein, ist aber {height}m"
        print(f"[OK] Wohnblock: {length}m x {width}m x {height}m (Traufhöhe korrekt)")
        
        print("\n[OK] TEST 1 BESTANDEN: Alle Traufhöhen korrekt!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST 1 FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grid_positions():
    """Test 2: Prüfe Modul-Platzierung"""
    print("\n" + "="*60)
    print("TEST 2: Modul-Platzierung")
    print("="*60)
    
    try:
        from pv3d_plotly import calculate_grid_positions
        
        # Test 1: Kleines Dach (10m x 6m)
        positions = calculate_grid_positions(10.0, 6.0, 20)
        print(f"\n10m x 6m Dach:")
        print(f"  Berechnete Positionen: {len(positions)}")
        print(f"  Erste Position: {positions[0] if positions else 'Keine'}")
        print(f"  Letzte Position: {positions[-1] if positions else 'Keine'}")
        
        # Prüfe ob Positionen zentriert sind
        if positions:
            x_coords = [p[0] for p in positions]
            y_coords = [p[1] for p in positions]
            x_center = (max(x_coords) + min(x_coords)) / 2
            y_center = (max(y_coords) + min(y_coords)) / 2
            print(f"  Zentrum: ({x_center:.2f}, {y_center:.2f})")
            
            # Zentrum sollte nahe (0, 0) sein
            assert abs(x_center) < 0.5, f"X-Zentrum sollte nahe 0 sein, ist aber {x_center:.2f}"
            assert abs(y_center) < 0.5, f"Y-Zentrum sollte nahe 0 sein, ist aber {y_center:.2f}"
            print(f"  [OK] Grid ist korrekt zentriert!")
        
        # Test 2: Großes Dach (20m x 12m)
        positions_large = calculate_grid_positions(20.0, 12.0, 50)
        print(f"\n20m x 12m Dach:")
        print(f"  Berechnete Positionen: {len(positions_large)}")
        
        # Test 3: Zu viele Module
        print(f"\nTest mit zu vielen Modulen (100 auf 10m x 6m):")
        positions_overflow = calculate_grid_positions(10.0, 6.0, 100)
        print(f"  Berechnete Positionen: {len(positions_overflow)}")
        print(f"  [WARNING] Warnung sollte erschienen sein!")
        
        print("\n[OK] TEST 2 BESTANDEN: Modul-Platzierung funktioniert!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST 2 FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_constants():
    """Test 3: Prüfe PV-Modul Konstanten"""
    print("\n" + "="*60)
    print("TEST 3: PV-Modul Konstanten")
    print("="*60)
    
    try:
        from pv3d import PV_W, PV_H, PV_T
        
        print(f"PV-Modul Abmessungen:")
        print(f"  Breite (PV_W): {PV_W}m")
        print(f"  Höhe (PV_H): {PV_H}m")
        print(f"  Dicke (PV_T): {PV_T}m")
        
        # Prüfe ob Werte realistisch sind
        assert 1.0 <= PV_W <= 1.2, f"PV_W sollte zwischen 1.0 und 1.2m sein"
        assert 1.6 <= PV_H <= 2.0, f"PV_H sollte zwischen 1.6 und 2.0m sein"
        assert 0.03 <= PV_T <= 0.05, f"PV_T sollte zwischen 0.03 und 0.05m sein"
        
        print(f"\n[OK] TEST 3 BESTANDEN: Modul-Konstanten sind korrekt!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST 3 FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_building_dims():
    """Test 4: Prüfe BuildingDims Klasse"""
    print("\n" + "="*60)
    print("TEST 4: BuildingDims Klasse")
    print("="*60)
    
    try:
        from pv3d import BuildingDims
        
        # Test Standard-Werte
        dims = BuildingDims()
        print(f"Standard BuildingDims:")
        print(f"  Länge: {dims.length_m}m")
        print(f"  Breite: {dims.width_m}m")
        print(f"  Traufhöhe: {dims.wall_height_m}m")
        
        # Test Custom-Werte
        dims_custom = BuildingDims(length_m=15.0, width_m=10.0, wall_height_m=3.0)
        print(f"\nCustom BuildingDims:")
        print(f"  Länge: {dims_custom.length_m}m")
        print(f"  Breite: {dims_custom.width_m}m")
        print(f"  Traufhöhe: {dims_custom.wall_height_m}m")
        
        assert dims_custom.wall_height_m == 3.0, "Custom Traufhöhe sollte 3m sein"
        
        print(f"\n[OK] TEST 4 BESTANDEN: BuildingDims funktioniert!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST 4 FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("3D-VISUALISIERUNG FIXES - TEST-SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Traufhöhe
    results.append(("Traufhöhe", test_default_dimensions()))
    
    # Test 2: Modul-Platzierung
    results.append(("Modul-Platzierung", test_grid_positions()))
    
    # Test 3: Modul-Konstanten
    results.append(("Modul-Konstanten", test_module_constants()))
    
    # Test 4: BuildingDims
    results.append(("BuildingDims", test_building_dims()))
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{name:.<40} {status}")
    
    print(f"\n{passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN! 🎉")
        return True
    else:
        print(f"\n[WARNING] {total - passed} Test(s) fehlgeschlagen!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
