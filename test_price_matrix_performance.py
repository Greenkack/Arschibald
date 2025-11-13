"""test_price_matrix_performance.py

Tests für Performance-Monitoring und Optimierung des Preismatrix-Systems.
"""

import time
from price_matrix_performance import (
    PerformanceMonitor,
    OperationMetrics,
    CacheMetrics,
    performance_tracked,
    get_global_monitor,
    reset_global_monitor,
    benchmark_matrix_lookup,
    analyze_cache_performance,
    get_memory_usage
)


def test_operation_metrics():
    """Test OperationMetrics Datenklasse"""
    print("\n=== Test: OperationMetrics ===")
    
    metrics = OperationMetrics("test_operation")
    
    # Erste Ausführung
    metrics.update(10.5, had_error=False)
    assert metrics.execution_count == 1
    assert metrics.total_time_ms == 10.5
    assert metrics.avg_time_ms == 10.5
    assert metrics.min_time_ms == 10.5
    assert metrics.max_time_ms == 10.5
    assert metrics.error_count == 0
    
    # Zweite Ausführung
    metrics.update(20.0, had_error=False)
    assert metrics.execution_count == 2
    assert metrics.total_time_ms == 30.5
    assert metrics.avg_time_ms == 15.25
    assert metrics.min_time_ms == 10.5
    assert metrics.max_time_ms == 20.0
    
    # Mit Fehler
    metrics.update(5.0, had_error=True)
    assert metrics.error_count == 1
    
    print("✅ OperationMetrics funktioniert korrekt")


def test_cache_metrics():
    """Test CacheMetrics Datenklasse"""
    print("\n=== Test: CacheMetrics ===")
    
    metrics = CacheMetrics("test_cache")
    
    # Hits registrieren
    metrics.update_hit(1.0)
    metrics.update_hit(2.0)
    metrics.update_hit(1.5)
    
    assert metrics.hit_count == 3
    assert metrics.miss_count == 0
    assert metrics.total_requests == 3
    assert metrics.hit_rate == 100.0
    
    # Misses registrieren
    metrics.update_miss(5.0)
    
    assert metrics.hit_count == 3
    assert metrics.miss_count == 1
    assert metrics.total_requests == 4
    assert metrics.hit_rate == 75.0
    
    print("✅ CacheMetrics funktioniert korrekt")


def test_performance_monitor():
    """Test PerformanceMonitor Klasse"""
    print("\n=== Test: PerformanceMonitor ===")
    
    monitor = PerformanceMonitor()
    
    # Operation tracken
    with monitor.track_operation('test_op'):
        time.sleep(0.01)  # 10ms
    
    assert 'test_op' in monitor.operations
    assert monitor.operations['test_op'].execution_count == 1
    
    # Mehrere Operationen
    for i in range(5):
        with monitor.track_operation('test_op'):
            time.sleep(0.001)
    
    assert monitor.operations['test_op'].execution_count == 6
    
    # Cache-Metriken
    monitor.record_cache_hit('test_cache', 0.5)
    monitor.record_cache_hit('test_cache', 0.3)
    monitor.record_cache_miss('test_cache', 2.0)
    
    assert 'test_cache' in monitor.caches
    assert monitor.caches['test_cache'].hit_count == 2
    assert monitor.caches['test_cache'].miss_count == 1
    assert monitor.caches['test_cache'].hit_rate == pytest.approx(66.67, rel=0.1)
    
    print("✅ PerformanceMonitor funktioniert korrekt")


def test_performance_report():
    """Test Bericht-Generierung"""
    print("\n=== Test: Performance-Bericht ===")
    
    monitor = PerformanceMonitor()
    
    # Simuliere Operationen
    for i in range(10):
        with monitor.track_operation('matrix_lookup'):
            time.sleep(0.001)
    
    # Simuliere Cache
    for i in range(20):
        if i < 15:
            monitor.record_cache_hit('matrix_cache', 0.1)
        else:
            monitor.record_cache_miss('matrix_cache', 1.0)
    
    # Generiere Bericht
    report = monitor.generate_report()
    
    assert 'PREISMATRIX PERFORMANCE BERICHT' in report
    assert 'matrix_lookup' in report
    assert 'matrix_cache' in report
    assert 'Hit-Rate' in report
    
    print("\n" + report)
    print("✅ Bericht-Generierung funktioniert")


def test_optimization_recommendations():
    """Test Optimierungsempfehlungen"""
    print("\n=== Test: Optimierungsempfehlungen ===")
    
    monitor = PerformanceMonitor()
    
    # Simuliere schlechte Cache-Performance
    for i in range(100):
        if i < 30:
            monitor.record_cache_hit('bad_cache', 0.1)
        else:
            monitor.record_cache_miss('bad_cache', 1.0)
    
    # Simuliere langsame Operation
    for i in range(10):
        monitor.record_operation('slow_operation', 150.0, had_error=False)
    
    # Hole Empfehlungen
    recommendations = monitor.get_optimization_recommendations()
    
    assert len(recommendations) > 0
    
    print("\nOptimierungsempfehlungen:")
    for rec in recommendations:
        print(f"  {rec}")
    
    print("✅ Optimierungsempfehlungen funktionieren")


def test_performance_decorator():
    """Test performance_tracked Decorator"""
    print("\n=== Test: Performance Decorator ===")
    
    reset_global_monitor()
    
    @performance_tracked('decorated_function')
    def test_function():
        time.sleep(0.01)
        return "result"
    
    # Funktion aufrufen
    result = test_function()
    assert result == "result"
    
    # Prüfe ob getrackt wurde
    monitor = get_global_monitor()
    assert 'decorated_function' in monitor.operations
    assert monitor.operations['decorated_function'].execution_count == 1
    
    print("✅ Performance Decorator funktioniert")


def test_benchmark_matrix_lookup():
    """Test Matrix-Lookup Benchmark"""
    print("\n=== Test: Matrix-Lookup Benchmark ===")
    
    # Erstelle Test-Matrix
    try:
        import price_matrix_store
        
        # Erstelle Matrix
        matrix_id = price_matrix_store.create_matrix("Benchmark Matrix")
        if matrix_id:
            # Füge Zeilen hinzu
            for count in [10, 15, 20]:
                price_matrix_store.add_row(matrix_id, str(count))
            
            # Füge Spalten hinzu
            for model in ["10kWh", "15kWh", "Kein Speicher"]:
                price_matrix_store.add_column(matrix_id, model)
            
            # Setze Preise
            rows = price_matrix_store.get_matrix_full(matrix_id)['rows']
            cols = price_matrix_store.get_matrix_full(matrix_id)['columns']
            
            for row in rows:
                for col in cols:
                    price_matrix_store.set_cell_value(
                        matrix_id, row['id'], col['id'], 15000.0
                    )
            
            # Aktiviere Matrix
            price_matrix_store.set_active_matrix(matrix_id)
            
            # Führe Benchmark durch
            results = benchmark_matrix_lookup(
                module_counts=[10, 15, 20],
                storage_models=["10kWh", "15kWh", None],
                iterations=10
            )
            
            print(f"\nBenchmark-Ergebnisse:")
            print(f"  Gesamt-Lookups: {results['total_lookups']}")
            print(f"  Erfolgreich: {results['successful_lookups']}")
            print(f"  Fehlgeschlagen: {results['failed_lookups']}")
            print(f"  Durchschnitt: {results['avg_time_ms']:.2f} ms")
            print(f"  Min: {results['min_time_ms']:.2f} ms")
            print(f"  Max: {results['max_time_ms']:.2f} ms")
            print(f"  Lookups/Sekunde: {results['lookups_per_second']:.0f}")
            
            assert results['total_lookups'] > 0
            assert results['avg_time_ms'] > 0
            
            # Cleanup
            price_matrix_store.delete_matrix(matrix_id)
            
            print("✅ Benchmark funktioniert")
        else:
            print("⚠️ Konnte Test-Matrix nicht erstellen, überspringe Benchmark")
    
    except ImportError:
        print("⚠️ price_matrix_store nicht verfügbar, überspringe Benchmark")


def test_cache_performance_analysis():
    """Test Cache-Performance-Analyse"""
    print("\n=== Test: Cache-Performance-Analyse ===")
    
    reset_global_monitor()
    monitor = get_global_monitor()
    
    # Simuliere Cache-Aktivität
    for i in range(100):
        if i < 80:
            monitor.record_cache_hit('matrix_cache', 0.5)
        else:
            monitor.record_cache_miss('matrix_cache', 2.0)
    
    monitor.update_cache_stats('matrix_cache', 10, 1024 * 1024)  # 1 MB
    
    # Analysiere
    analysis = analyze_cache_performance()
    
    print(f"\nCache-Analyse:")
    print(f"  Gesamt Hit-Rate: {analysis['overall_hit_rate']:.1f}%")
    print(f"  Gesamt Speicher: {analysis['total_memory_mb']:.2f} MB")
    
    for cache_name, info in analysis['caches'].items():
        print(f"\n  {cache_name}:")
        print(f"    Hit-Rate: {info['hit_rate']:.1f}%")
        print(f"    Anfragen: {info['total_requests']}")
        print(f"    Einträge: {info['entry_count']}")
        print(f"    Speicher: {info['memory_mb']:.2f} MB")
    
    assert analysis['overall_hit_rate'] > 0
    assert 'matrix_cache' in analysis['caches']
    
    print("✅ Cache-Analyse funktioniert")


def test_memory_usage():
    """Test Speicherverbrauch-Analyse"""
    print("\n=== Test: Speicherverbrauch ===")
    
    memory = get_memory_usage()
    
    print(f"\nSpeicherverbrauch:")
    print(f"  Prozess-Speicher: {memory['process_memory_mb']:.2f} MB")
    print(f"  Matrix-Cache: {memory['matrix_cache_mb']:.2f} MB")
    print(f"  Objekte: {memory['total_objects']}")
    
    assert memory['total_objects'] > 0
    
    print("✅ Speicherverbrauch-Analyse funktioniert")


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 70)
    print("PREISMATRIX PERFORMANCE TESTS")
    print("=" * 70)
    
    try:
        test_operation_metrics()
        test_cache_metrics()
        test_performance_monitor()
        test_performance_report()
        test_optimization_recommendations()
        test_performance_decorator()
        test_benchmark_matrix_lookup()
        test_cache_performance_analysis()
        test_memory_usage()
        
        print("\n" + "=" * 70)
        print("✅ ALLE TESTS ERFOLGREICH")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNERWARTETER FEHLER: {e}")
        raise


if __name__ == "__main__":
    # pytest importieren falls verfügbar
    try:
        import pytest
    except ImportError:
        # Fallback für pytest.approx
        class ApproxHelper:
            def __init__(self, value, rel=0.01):
                self.value = value
                self.rel = rel
            
            def __eq__(self, other):
                return abs(self.value - other) / self.value <= self.rel
        
        class PytestMock:
            @staticmethod
            def approx(value, rel=0.01):
                return ApproxHelper(value, rel)
        
        pytest = PytestMock()
    
    run_all_tests()
