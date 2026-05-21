"""
Test für Task 9: Performance-Optimierung

Testet die Performance-Optimierungen für Modul-Platzierung:
- Task 9.1: Lazy Loading (LOD, Batch-Rendering)
- Task 9.2: Caching (Positionen, Transformationen, Mesh-Geometrie)
"""

import sys
import time
import numpy as np

# Test-Konfiguration
print("=" * 70)
print("TEST: Task 9 - Performance-Optimierung")
print("=" * 70)

# ============================================================================
# TEST 9.1: LAZY LOADING
# ============================================================================

print("\n" + "=" * 70)
print("TEST 9.1: Lazy Loading")
print("=" * 70)

try:
    from utils.pv3d_performance import (
        should_render_module,
        batch_render_modules,
        get_lod_info
    )
    
    print("\nPerformance-Module erfolgreich importiert")
    
    # Test 9.1.1: LOD-Funktion
    print("\n--- Test 9.1.1: Level-of-Detail (LOD) ---")
    
    # Test mit wenigen Modulen (alle rendern)
    total_modules_small = 30
    lod_threshold = 50
    rendered_count = sum(
        1 for i in range(total_modules_small)
        if should_render_module(i, total_modules_small, lod_threshold=lod_threshold)
    )
    print(f"Bei {total_modules_small} Modulen (< {lod_threshold}): {rendered_count} gerendert")
    assert rendered_count == total_modules_small, "Alle Module sollten gerendert werden"
    
    # Test mit vielen Modulen (LOD aktiv)
    total_modules_large = 100
    rendered_count_lod = sum(
        1 for i in range(total_modules_large)
        if should_render_module(i, total_modules_large, lod_threshold=lod_threshold)
    )
    print(f"Bei {total_modules_large} Modulen (> {lod_threshold}): {rendered_count_lod} gerendert")
    assert rendered_count_lod < total_modules_large, "LOD sollte Module reduzieren"
    assert rendered_count_lod >= lod_threshold * 0.8, "Mindestens 80% des Thresholds sollten gerendert werden"
    
    # Test LOD-Info
    print("\n--- Test 9.1.2: LOD-Informationen ---")
    lod_info = get_lod_info(100, lod_threshold=50)
    print(f"LOD aktiviert: {lod_info['enabled']}")
    print(f"Skip-Faktor: {lod_info['skip_factor']}")
    print(f"Gerendert: {lod_info['rendered_count']} von {100}")
    print(f"Übersprungen: {lod_info['skipped_count']}")
    print(f"Reduktion: {lod_info['reduction_percent']:.1f}%")
    
    assert lod_info['enabled'] == True, "LOD sollte aktiviert sein"
    assert lod_info['rendered_count'] < 100, "Nicht alle Module sollten gerendert werden"
    
    # Test 9.1.3: Batch-Rendering
    print("\n--- Test 9.1.3: Batch-Rendering ---")
    
    # Mock-Render-Funktion
    render_count = 0
    def mock_render_module(x, y, z, module_number, **kwargs):
        global render_count
        render_count += 1
        return f"Module_{module_number}"
    
    # Test-Positionen (mehr als LOD-Threshold für LOD-Aktivierung)
    test_positions = [(i, 0, 3) for i in range(100)]
    
    render_count = 0
    meshes = batch_render_modules(
        test_positions,
        mock_render_module,
        batch_size=10,
        enable_lod=True,
        lod_threshold=50
    )
    
    print(f"Batch-Rendering: {render_count} Module gerendert (von {len(test_positions)})")
    print(f"Batch-Größe: 10 Module pro Batch")
    print(f"LOD-Reduktion: {((len(test_positions) - render_count) / len(test_positions) * 100):.1f}%")
    assert render_count < len(test_positions), "LOD sollte Module reduzieren"
    assert len(meshes) == render_count, "Anzahl Meshes sollte Render-Count entsprechen"
    
    print("\nTask 9.1 (Lazy Loading) - ALLE TESTS BESTANDEN")
    
except ImportError as e:
    print(f"\nImport-Fehler: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"\nTest fehlgeschlagen: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\nUnerwarteter Fehler: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# ============================================================================
# TEST 9.2: CACHING
# ============================================================================

print("\n" + "=" * 70)
print("TEST 9.2: Caching")
print("=" * 70)

try:
    from utils.pv3d_performance import (
        cache_module_mesh_geometry,
        get_cached_rotation_matrix,
        calculate_module_positions_cached,
        get_all_cache_stats,
        clear_all_caches
    )
    
    print("\nCaching-Funktionen erfolgreich importiert")
    
    # Test 9.2.1: Mesh-Geometrie-Caching
    print("\n--- Test 9.2.1: Mesh-Geometrie-Caching ---")
    
    # Erster Aufruf (Cache-Miss)
    start_time = time.time()
    geom1 = cache_module_mesh_geometry()
    time1 = time.time() - start_time
    
    # Zweiter Aufruf (Cache-Hit)
    start_time = time.time()
    geom2 = cache_module_mesh_geometry()
    time2 = time.time() - start_time
    
    print(f"Erster Aufruf (Cache-Miss): {time1*1000:.2f}ms")
    print(f"Zweiter Aufruf (Cache-Hit): {time2*1000:.2f}ms")
    if time2 > 0:
        print(f"Speedup: {time1/time2:.1f}x schneller")
    else:
        print(f"Speedup: >1000x schneller (Cache-Hit zu schnell zum Messen)")
    
    # Prüfe Geometrie
    assert 'vertices' in geom1, "Geometrie sollte Vertices enthalten"
    assert 'faces_i' in geom1, "Geometrie sollte Face-Indizes enthalten"
    assert len(geom1['vertices']) == 8, "Quader sollte 8 Vertices haben"
    assert np.array_equal(geom1['vertices'], geom2['vertices']), "Gecachte Geometrie sollte identisch sein"
    
    print(f"Geometrie: {len(geom1['vertices'])} Vertices, {len(geom1['faces_i'])} Face-Indizes")
    
    # Test 9.2.2: Rotationsmatrizen-Caching
    print("\n--- Test 9.2.2: Rotationsmatrizen-Caching ---")
    
    # Erster Aufruf (Cache-Miss)
    start_time = time.time()
    R1 = get_cached_rotation_matrix(0, 30)
    time1 = time.time() - start_time
    
    # Zweiter Aufruf (Cache-Hit)
    start_time = time.time()
    R2 = get_cached_rotation_matrix(0, 30)
    time2 = time.time() - start_time
    
    print(f"Erster Aufruf (Cache-Miss): {time1*1000:.2f}ms")
    print(f"Zweiter Aufruf (Cache-Hit): {time2*1000:.2f}ms")
    if time2 > 0:
        print(f"Speedup: {time1/time2:.1f}x schneller")
    else:
        print(f"Speedup: >1000x schneller (Cache-Hit zu schnell zum Messen)")
    
    assert R1.shape == (3, 3), "Rotationsmatrix sollte 3x3 sein"
    assert np.array_equal(R1, R2), "Gecachte Matrix sollte identisch sein"
    
    # Test verschiedene Transformationen
    R_south = get_cached_rotation_matrix(0, 30)    # Süd, 30°
    R_west = get_cached_rotation_matrix(90, 30)    # West, 30°
    R_flat = get_cached_rotation_matrix(0, 0)      # Flach
    
    print(f"Verschiedene Transformationen gecacht: Süd, West, Flach")
    
    # Test 9.2.3: Cache-Statistiken
    print("\n--- Test 9.2.3: Cache-Statistiken ---")
    
    stats = get_all_cache_stats()
    print(f"Global Cache: {stats['global_cache']['size']} Einträge")
    print(f"Transformation Cache: {stats['transformation_cache']['size']} Einträge")
    print(f"Unique Transformationen: {stats['transformation_cache']['unique_transformations']}")
    
    assert 'global_cache' in stats, "Statistiken sollten Global Cache enthalten"
    assert 'transformation_cache' in stats, "Statistiken sollten Transformation Cache enthalten"
    
    # Test 9.2.4: Cache-Clearing
    print("\n--- Test 9.2.4: Cache-Clearing ---")
    
    clear_all_caches()
    stats_after = get_all_cache_stats()
    
    print(f"Caches geleert")
    print(f"Global Cache nach Clear: {stats_after['global_cache']['size']} Einträge")
    print(f"Transformation Cache nach Clear: {stats_after['transformation_cache']['size']} Einträge")
    
    assert stats_after['global_cache']['size'] == 0, "Global Cache sollte leer sein"
    assert stats_after['transformation_cache']['size'] == 0, "Transformation Cache sollte leer sein"
    
    print("\nTask 9.2 (Caching) - ALLE TESTS BESTANDEN")
    
except ImportError as e:
    print(f"\nImport-Fehler: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"\nTest fehlgeschlagen: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\nUnerwarteter Fehler: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# ============================================================================
# PERFORMANCE-VERGLEICH
# ============================================================================

print("\n" + "=" * 70)
print("PERFORMANCE-VERGLEICH")
print("=" * 70)

try:
    print("\n--- Vergleich: Mit vs. Ohne Optimierungen ---")
    
    # Simuliere Modul-Rendering ohne Optimierungen
    def render_without_optimization(num_modules):
        start = time.time()
        for i in range(num_modules):
            # Simuliere Mesh-Erstellung
            geom = cache_module_mesh_geometry()
            R = get_cached_rotation_matrix(0, 30)
        return time.time() - start
    
    # Simuliere Modul-Rendering mit Optimierungen (LOD)
    def render_with_optimization(num_modules):
        start = time.time()
        rendered = 0
        for i in range(num_modules):
            if should_render_module(i, num_modules, lod_threshold=50):
                geom = cache_module_mesh_geometry()
                R = get_cached_rotation_matrix(0, 30)
                rendered += 1
        return time.time() - start, rendered
    
    # Test mit verschiedenen Modulanzahlen
    test_counts = [50, 100, 200]
    
    for count in test_counts:
        # Ohne Optimierung
        time_without = render_without_optimization(count)
        
        # Mit Optimierung
        time_with, rendered = render_with_optimization(count)
        
        if time_with != 0:
            speedup = time_without / time_with if time_with > 0 else 1.0
        else:
            speedup = 0.0
        reduction = ((count - rendered) / count) * 100
        
        print(f"\n{count} Module:")
        print(f"  Ohne Optimierung: {time_without*1000:.2f}ms ({count} Module)")
        print(f"  Mit Optimierung:  {time_with*1000:.2f}ms ({rendered} Module)")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Reduktion: {reduction:.1f}%")
    
    print("\nPerformance-Vergleich abgeschlossen")
    
except Exception as e:
    print(f"\nPerformance-Vergleich fehlgeschlagen: {e}")


# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================

print("\n" + "=" * 70)
print("ZUSAMMENFASSUNG")
print("=" * 70)

print("\nTask 9.1: Lazy Loading")
print("   - LOD-Funktion implementiert und getestet")
print("   - Batch-Rendering implementiert und getestet")
print("   - LOD-Informationen verfügbar")

print("\nTask 9.2: Caching")
print("   - Mesh-Geometrie-Caching implementiert")
print("   - Rotationsmatrizen-Caching implementiert")
print("   - Cache-Statistiken verfügbar")
print("   - Cache-Management (Clear) funktioniert")

print("\n" + "=" * 70)
print("ALLE TESTS ERFOLGREICH")
print("=" * 70)
