"""
Test-Datei für Performance-Optimierungen

Testet alle Performance-Features:
- Caching
- Debouncing
- Lazy Loading
- Performance-Monitoring
"""

import time
import sys
from utils.pv3d_performance import (
    cached,
    monitor_performance,
    get_cache_stats,
    clear_cache,
    get_performance_stats,
    clear_performance_stats,
    Debouncer,
    PerformanceCache,
    optimize_mesh_resolution,
    should_render_module
)


def test_caching():
    """Testet Caching-Funktionalität."""
    print("\n" + "="*60)
    print("TEST 1: CACHING")
    print("="*60)
    
    # Definiere teure Funktion
    call_count = [0]
    
    @cached(ttl=5.0)
    def expensive_calculation(x, y):
        call_count[0] += 1
        time.sleep(0.1)  # Simuliere teure Berechnung
        return x ** y
    
    # Erster Aufruf - sollte berechnet werden
    print("\n1. Erster Aufruf (sollte berechnet werden):")
    start = time.time()
    result1 = expensive_calculation(2, 10)
    duration1 = time.time() - start
    print(f"   Ergebnis: {result1}")
    print(f"   Dauer: {duration1:.3f}s")
    print(f"   Aufrufe: {call_count[0]}")
    
    # Zweiter Aufruf - sollte aus Cache kommen
    print("\n2. Zweiter Aufruf (sollte aus Cache kommen):")
    start = time.time()
    result2 = expensive_calculation(2, 10)
    duration2 = time.time() - start
    print(f"   Ergebnis: {result2}")
    print(f"   Dauer: {duration2:.3f}s")
    print(f"   Aufrufe: {call_count[0]}")
    
    # Prüfe Ergebnisse
    assert result1 == result2, "Ergebnisse sollten gleich sein"
    assert call_count[0] == 1, "Funktion sollte nur einmal aufgerufen werden"
    assert duration2 < duration1 / 10, "Cache sollte viel schneller sein"
    
    # Cache-Statistiken
    stats = get_cache_stats()
    print(f"\n3. Cache-Statistiken:")
    print(f"   Einträge: {stats['entries']}")
    print(f"   Hits: {stats['total_hits']}")
    
    # Cache leeren
    clear_cache()
    print("\n4. Cache geleert")
    
    # Dritter Aufruf - sollte wieder berechnet werden
    print("\n5. Dritter Aufruf nach Cache-Clear (sollte berechnet werden):")
    start = time.time()
    result3 = expensive_calculation(2, 10)
    duration3 = time.time() - start
    print(f"   Ergebnis: {result3}")
    print(f"   Dauer: {duration3:.3f}s")
    print(f"   Aufrufe: {call_count[0]}")
    
    assert call_count[0] == 2, "Funktion sollte zweimal aufgerufen werden"
    
    print("\n[OK] Caching-Test erfolgreich!")


def test_debouncing():
    """Testet Debouncing-Funktionalität."""
    print("\n" + "="*60)
    print("TEST 2: DEBOUNCING")
    print("="*60)
    
    debouncer = Debouncer(delay=0.5)
    
    # Schnelle Änderungen - sollten gedebounced werden
    print("\n1. Schnelle Änderungen (sollten gedebounced werden):")
    
    values = [1, 2, 3, 4, 5]
    updates = []
    
    for i, value in enumerate(values):
        result, should_update = debouncer.debounce("test_key", value)
        updates.append(should_update)
        print(f"   Wert {value}: should_update={should_update}, result={result}")
        
        if i < len(values) - 1:
            time.sleep(0.1)  # Kurze Pause (< delay)
    
    # Nur erster Aufruf sollte Update auslösen
    assert updates[0] == True, "Erster Aufruf sollte Update auslösen"
    assert all(not u for u in updates[1:]), "Weitere Aufrufe sollten kein Update auslösen"
    
    # Warte Debounce-Zeit ab
    print("\n2. Warte Debounce-Zeit ab...")
    time.sleep(0.6)
    
    # Nächster Aufruf sollte Update auslösen
    print("\n3. Aufruf nach Debounce-Zeit (sollte Update auslösen):")
    result, should_update = debouncer.debounce("test_key", 6)
    print(f"   Wert 6: should_update={should_update}, result={result}")
    
    assert should_update == True, "Aufruf nach Debounce-Zeit sollte Update auslösen"
    
    print("\n[OK] Debouncing-Test erfolgreich!")


def test_performance_monitoring():
    """Testet Performance-Monitoring."""
    print("\n" + "="*60)
    print("TEST 3: PERFORMANCE-MONITORING")
    print("="*60)
    
    # Definiere überwachte Funktion
    @monitor_performance("test_operation")
    def monitored_function(duration):
        time.sleep(duration)
        return "done"
    
    # Führe Funktion mehrmals aus
    print("\n1. Führe überwachte Funktion aus:")
    durations = [0.1, 0.2, 0.15]
    
    for i, duration in enumerate(durations):
        print(f"   Aufruf {i+1}: {duration}s")
        monitored_function(duration)
    
    # Hole Statistiken
    stats = get_performance_stats()
    print("\n2. Performance-Statistiken:")
    
    if "test_operation" in stats:
        op_stats = stats["test_operation"]
        print(f"   Anzahl: {op_stats['count']}")
        print(f"   Min: {op_stats['min']:.3f}s")
        print(f"   Max: {op_stats['max']:.3f}s")
        print(f"   Avg: {op_stats['avg']:.3f}s")
        print(f"   Total: {op_stats['total']:.3f}s")
        
        # Prüfe Werte
        assert op_stats['count'] == 3, "Sollte 3 Aufrufe haben"
        assert 0.09 < op_stats['min'] < 0.11, "Min sollte ~0.1s sein"
        assert 0.19 < op_stats['max'] < 0.21, "Max sollte ~0.2s sein"
    else:
        print("   ⚠️ Keine Statistiken gefunden")
    
    # Statistiken leeren
    clear_performance_stats()
    print("\n3. Statistiken geleert")
    
    print("\n[OK] Performance-Monitoring-Test erfolgreich!")


def test_mesh_optimization():
    """Testet Mesh-Optimierungen."""
    print("\n" + "="*60)
    print("TEST 4: MESH-OPTIMIERUNG")
    print("="*60)
    
    # Teste optimize_mesh_resolution
    print("\n1. Teste optimize_mesh_resolution:")
    
    test_cases = [
        (5000, 1.0),    # Wenige Vertices -> volle Auflösung
        (10000, 1.0),   # Genau am Limit -> volle Auflösung
        (20000, 0.5),   # Doppelt so viele -> halbe Auflösung
        (50000, 0.3),   # Viel zu viele -> minimale Auflösung
    ]
    
    for vertex_count, expected_scale in test_cases:
        scale = optimize_mesh_resolution(vertex_count)
        print(f"   {vertex_count} Vertices -> Scale: {scale:.2f} (erwartet: {expected_scale:.2f})")
        assert abs(scale - expected_scale) < 0.1, f"Scale sollte ~{expected_scale} sein"
    
    # Teste should_render_module
    print("\n2. Teste should_render_module (LOD):")
    
    # Wenige Module - alle rendern
    total_modules = 30
    rendered = sum(1 for i in range(total_modules) if should_render_module(i, total_modules, 10.0))
    print(f"   {total_modules} Module -> {rendered} gerendert (alle)")
    assert rendered == total_modules, "Alle Module sollten gerendert werden"
    
    # Viele Module - nur jeden N-ten rendern
    total_modules = 200
    rendered = sum(1 for i in range(total_modules) if should_render_module(i, total_modules, 10.0))
    print(f"   {total_modules} Module -> {rendered} gerendert (LOD)")
    assert rendered < total_modules, "Nicht alle Module sollten gerendert werden"
    assert rendered >= 50, "Mindestens 50 Module sollten gerendert werden"
    
    print("\n[OK] Mesh-Optimierung-Test erfolgreich!")


def test_cache_ttl():
    """Testet Cache TTL (Time To Live)."""
    print("\n" + "="*60)
    print("TEST 5: CACHE TTL")
    print("="*60)
    
    cache = PerformanceCache(max_size=10, default_ttl=1.0)  # 1 Sekunde TTL
    
    # Speichere Wert
    print("\n1. Speichere Wert im Cache:")
    cache.set("test_key", "test_value")
    print("   Wert gespeichert")
    
    # Hole Wert sofort - sollte funktionieren
    print("\n2. Hole Wert sofort:")
    value = cache.get("test_key")
    print(f"   Wert: {value}")
    assert value == "test_value", "Wert sollte aus Cache kommen"
    
    # Warte TTL ab
    print("\n3. Warte TTL ab (1.5s)...")
    time.sleep(1.5)
    
    # Hole Wert nach TTL - sollte None sein
    print("\n4. Hole Wert nach TTL:")
    value = cache.get("test_key")
    print(f"   Wert: {value}")
    assert value is None, "Wert sollte abgelaufen sein"
    
    print("\n[OK] Cache TTL-Test erfolgreich!")


def test_cache_lru():
    """Testet Cache LRU (Least Recently Used) Eviction."""
    print("\n" + "="*60)
    print("TEST 6: CACHE LRU")
    print("="*60)
    
    cache = PerformanceCache(max_size=3, default_ttl=60.0)
    
    # Fülle Cache
    print("\n1. Fülle Cache (max_size=3):")
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    print("   3 Werte gespeichert")
    
    # Prüfe Größe
    stats = cache.get_stats()
    print(f"   Cache-Größe: {stats['size']}")
    assert stats['size'] == 3, "Cache sollte 3 Einträge haben"
    
    # Füge vierten Wert hinzu - sollte ältesten entfernen
    print("\n2. Füge vierten Wert hinzu (sollte key1 entfernen):")
    cache.set("key4", "value4")
    
    # Prüfe ob key1 entfernt wurde
    value1 = cache.get("key1")
    value4 = cache.get("key4")
    print(f"   key1: {value1} (sollte None sein)")
    print(f"   key4: {value4} (sollte value4 sein)")
    
    assert value1 is None, "key1 sollte entfernt worden sein"
    assert value4 == "value4", "key4 sollte vorhanden sein"
    
    # Prüfe Größe
    stats = cache.get_stats()
    print(f"   Cache-Größe: {stats['size']}")
    assert stats['size'] == 3, "Cache sollte immer noch 3 Einträge haben"
    
    print("\n[OK] Cache LRU-Test erfolgreich!")


def run_all_tests():
    """Führt alle Tests aus."""
    print("\n" + "="*60)
    print("PERFORMANCE-OPTIMIERUNGEN TESTS")
    print("="*60)
    
    try:
        test_caching()
        test_debouncing()
        test_performance_monitoring()
        test_mesh_optimization()
        test_cache_ttl()
        test_cache_lru()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALLE TESTS ERFOLGREICH!")
        print("="*60)

        return True

    except AssertionError as e:
        print(f"\n[FAIL] TEST FEHLGESCHLAGEN: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
