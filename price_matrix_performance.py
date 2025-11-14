"""price_matrix_performance.py

Performance-Monitoring und Optimierung für das Preismatrix-System.

Dieses Modul bietet:
- Performance-Metriken für Matrix-Operationen
- Cache-Performance-Analyse
- Optimierungsempfehlungen
- Benchmark-Tools
- Memory-Profiling

Verwendung:
    from price_matrix_performance import (
        PerformanceMonitor,
        benchmark_matrix_lookup,
        analyze_cache_performance,
        get_optimization_recommendations
    )
    
    # Performance-Monitoring aktivieren
    monitor = PerformanceMonitor()
    
    # Matrix-Lookup mit Monitoring
    with monitor.track_operation('matrix_lookup'):
        result = calculate_price_from_matrix(20, "15kWh")
    
    # Performance-Bericht anzeigen
    report = monitor.generate_report()
    print(report)
"""

import time
import functools
import hashlib
import sys
from typing import Any, Callable, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class OperationMetrics:
    """Metriken für eine einzelne Operation"""
    operation_name: str
    execution_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    last_execution: Optional[datetime] = None
    error_count: int = 0
    
    def update(self, execution_time_ms: float, had_error: bool = False):
        """Aktualisiert Metriken mit neuer Ausführung"""
        self.execution_count += 1
        self.total_time_ms += execution_time_ms
        self.min_time_ms = min(self.min_time_ms, execution_time_ms)
        self.max_time_ms = max(self.max_time_ms, execution_time_ms)
        if self != 0:
            self.avg_time_ms = self.total_time_ms / self.execution_count
        else:
            self.avg_time_ms = 0.0
        self.last_execution = datetime.now()
        if had_error:
            self.error_count += 1


@dataclass
class CacheMetrics:
    """Metriken für Cache-Performance"""
    cache_name: str
    hit_count: int = 0
    miss_count: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    avg_lookup_time_ms: float = 0.0
    memory_usage_bytes: int = 0
    entry_count: int = 0
    eviction_count: int = 0
    
    def update_hit(self, lookup_time_ms: float = 0.0):
        """Registriert Cache-Hit"""
        self.hit_count += 1
        self.total_requests += 1
        self._recalculate_hit_rate()
        self._update_avg_lookup_time(lookup_time_ms)
    
    def update_miss(self, lookup_time_ms: float = 0.0):
        """Registriert Cache-Miss"""
        self.miss_count += 1
        self.total_requests += 1
        self._recalculate_hit_rate()
        self._update_avg_lookup_time(lookup_time_ms)
    
    def _recalculate_hit_rate(self):
        """Berechnet Hit-Rate neu"""
        if self.total_requests > 0:
            if self != 0:
                self.hit_rate = (self.hit_count / self.total_requests) * 100
            else:
                self.hit_rate = 0.0
    
    def _update_avg_lookup_time(self, lookup_time_ms: float):
        """Aktualisiert durchschnittliche Lookup-Zeit"""
        if self.total_requests > 0:
            total_time = self.avg_lookup_time_ms * (self.total_requests - 1)
            self.avg_lookup_time_ms = (total_time + lookup_time_ms) / self.total_requests


class PerformanceMonitor:
    """
    Zentrale Performance-Monitoring Klasse für Preismatrix-Operationen.
    
    Beispiel:
        monitor = PerformanceMonitor()
        
        # Operation tracken
        with monitor.track_operation('matrix_lookup'):
            result = calculate_price_from_matrix(20, "15kWh")
        
        # Bericht generieren
        report = monitor.generate_report()
    """
    
    def __init__(self):
        self.operations: dict[str, OperationMetrics] = {}
        self.caches: dict[str, CacheMetrics] = {}
        self.start_time = datetime.now()
        self.enabled = True
    
    def track_operation(self, operation_name: str):
        """Context Manager für Operation-Tracking"""
        return OperationTracker(self, operation_name)
    
    def record_operation(
        self,
        operation_name: str,
        execution_time_ms: float,
        had_error: bool = False
    ):
        """Registriert eine Operation"""
        if not self.enabled:
            return
        
        if operation_name not in self.operations:
            self.operations[operation_name] = OperationMetrics(operation_name)
        
        self.operations[operation_name].update(execution_time_ms, had_error)
    
    def record_cache_hit(self, cache_name: str, lookup_time_ms: float = 0.0):
        """Registriert Cache-Hit"""
        if not self.enabled:
            return
        
        if cache_name not in self.caches:
            self.caches[cache_name] = CacheMetrics(cache_name)
        
        self.caches[cache_name].update_hit(lookup_time_ms)
    
    def record_cache_miss(self, cache_name: str, lookup_time_ms: float = 0.0):
        """Registriert Cache-Miss"""
        if not self.enabled:
            return
        
        if cache_name not in self.caches:
            self.caches[cache_name] = CacheMetrics(cache_name)
        
        self.caches[cache_name].update_miss(lookup_time_ms)
    
    def update_cache_stats(
        self,
        cache_name: str,
        entry_count: int,
        memory_usage_bytes: int
    ):
        """Aktualisiert Cache-Statistiken"""
        if not self.enabled:
            return
        
        if cache_name not in self.caches:
            self.caches[cache_name] = CacheMetrics(cache_name)
        
        self.caches[cache_name].entry_count = entry_count
        self.caches[cache_name].memory_usage_bytes = memory_usage_bytes
    
    def generate_report(self, detailed: bool = True) -> str:
        """
        Generiert Performance-Bericht.
        
        Args:
            detailed: Wenn True, zeigt detaillierte Metriken
        
        Returns:
            Formatierter Bericht als String
        """
        lines = []
        lines.append("=" * 70)
        lines.append("PREISMATRIX PERFORMANCE BERICHT")
        lines.append("=" * 70)
        
        # Laufzeit
        uptime = datetime.now() - self.start_time
        lines.append(f"\nMonitoring-Laufzeit: {uptime}")
        lines.append("")
        
        # Operations-Metriken
        if self.operations:
            lines.append("OPERATIONS-METRIKEN")
            lines.append("-" * 70)
            
            for op_name, metrics in sorted(
                self.operations.items(),
                key=lambda x: x[1].total_time_ms,
                reverse=True
            ):
                lines.append(f"\n{op_name}:")
                lines.append(f"  Ausführungen: {metrics.execution_count}")
                lines.append(f"  Gesamt-Zeit: {metrics.total_time_ms:.2f} ms")
                lines.append(f"  Durchschnitt: {metrics.avg_time_ms:.2f} ms")
                lines.append(f"  Min: {metrics.min_time_ms:.2f} ms")
                lines.append(f"  Max: {metrics.max_time_ms:.2f} ms")
                
                if metrics.error_count > 0:
                    if metrics != 0:
                        error_rate = (metrics.error_count / metrics.execution_count) * 100
                    else:
                        error_rate = 0.0
                    lines.append(f"  Fehler: {metrics.error_count} ({error_rate:.1f}%)")
        
        # Cache-Metriken
        if self.caches:
            lines.append("\n\nCACHE-METRIKEN")
            lines.append("-" * 70)
            
            for cache_name, metrics in self.caches.items():
                lines.append(f"\n{cache_name}:")
                lines.append(f"  Anfragen: {metrics.total_requests}")
                lines.append(f"  Hits: {metrics.hit_count}")
                lines.append(f"  Misses: {metrics.miss_count}")
                lines.append(f"  Hit-Rate: {metrics.hit_rate:.1f}%")
                lines.append(f"  Einträge: {metrics.entry_count}")
                
                if metrics.memory_usage_bytes > 0:
                    mb = metrics.memory_usage_bytes / (1024 * 1024)
                    lines.append(f"  Speicher: {mb:.2f} MB")
                
                if metrics.avg_lookup_time_ms > 0:
                    lines.append(f"  Ø Lookup-Zeit: {metrics.avg_lookup_time_ms:.2f} ms")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
    
    def get_optimization_recommendations(self) -> list[str]:
        """
        Analysiert Metriken und gibt Optimierungsempfehlungen.
        
        Returns:
            Liste von Empfehlungen
        """
        recommendations = []
        
        # Analysiere Cache-Performance
        for cache_name, metrics in self.caches.items():
            if metrics.total_requests > 100:
                if metrics.hit_rate < 50:
                    recommendations.append(
                        f"[WARNING] {cache_name}: Niedrige Hit-Rate ({metrics.hit_rate:.1f}%). "
                        "Erwägen Sie Cache-Größe zu erhöhen oder TTL anzupassen."
                    )
                elif metrics.hit_rate > 95:
                    recommendations.append(
                        f"[OK] {cache_name}: Exzellente Hit-Rate ({metrics.hit_rate:.1f}%)!"
                    )
        
        # Analysiere langsame Operationen
        for op_name, metrics in self.operations.items():
            if metrics.avg_time_ms > 100:
                recommendations.append(
                    f"[WARNING] {op_name}: Langsame Operation (Ø {metrics.avg_time_ms:.1f} ms). "
                    "Prüfen Sie auf Optimierungspotential."
                )
            
            if metrics.error_count > 0:
                if metrics != 0:
                    error_rate = (metrics.error_count / metrics.execution_count) * 100
                else:
                    error_rate = 0.0
                if error_rate > 5:
                    recommendations.append(
                        f"[ERROR] {op_name}: Hohe Fehlerrate ({error_rate:.1f}%). "
                        "Fehlerbehandlung überprüfen."
                    )
        
        # Allgemeine Empfehlungen
        total_operations = sum(m.execution_count for m in self.operations.values())
        if total_operations > 1000:
            recommendations.append(
                "[IDEA] Hohe Anzahl an Operationen. Erwägen Sie Batch-Processing."
            )
        
        if not recommendations:
            recommendations.append("[OK] Keine Optimierungen erforderlich. System läuft optimal!")
        
        return recommendations
    
    def reset(self):
        """Setzt alle Metriken zurück"""
        self.operations.clear()
        self.caches.clear()
        self.start_time = datetime.now()


class OperationTracker:
    """Context Manager für Operation-Tracking"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        self.had_error = False
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time_ms = (time.time() - self.start_time) * 1000
        self.had_error = exc_type is not None
        self.monitor.record_operation(
            self.operation_name,
            execution_time_ms,
            self.had_error
        )
        return False  # Don't suppress exceptions


def performance_tracked(operation_name: str):
    """
    Decorator für automatisches Performance-Tracking.
    
    Beispiel:
        @performance_tracked('matrix_lookup')
        def my_function():
            # ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Hole globalen Monitor
            monitor = get_global_monitor()
            
            with monitor.track_operation(operation_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Globaler Monitor
_global_monitor: Optional[PerformanceMonitor] = None


def get_global_monitor() -> PerformanceMonitor:
    """Holt oder erstellt globalen Performance-Monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def reset_global_monitor():
    """Setzt globalen Monitor zurück"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.reset()


def benchmark_matrix_lookup(
    module_counts: list[int],
    storage_models: list[str],
    iterations: int = 100
) -> dict[str, Any]:
    """
    Benchmark für Matrix-Lookup Performance.
    
    Args:
        module_counts: Liste von Modulanzahlen zum Testen
        storage_models: Liste von Speichermodellen zum Testen
        iterations: Anzahl Wiederholungen pro Kombination
    
    Returns:
        Benchmark-Ergebnisse
    """
    from price_matrix_lookup import calculate_price_from_matrix
    
    results = {
        'total_lookups': 0,
        'successful_lookups': 0,
        'failed_lookups': 0,
        'total_time_ms': 0.0,
        'avg_time_ms': 0.0,
        'min_time_ms': float('inf'),
        'max_time_ms': 0.0,
        'lookups_per_second': 0.0
    }
    
    start_time = time.time()
    
    for _ in range(iterations):
        for module_count in module_counts:
            for storage_model in storage_models:
                lookup_start = time.time()
                
                result = calculate_price_from_matrix(
                    module_count,
                    storage_model,
                    enable_fallback=False
                )
                
                lookup_time_ms = (time.time() - lookup_start) * 1000
                
                results['total_lookups'] += 1
                results['total_time_ms'] += lookup_time_ms
                results['min_time_ms'] = min(results['min_time_ms'], lookup_time_ms)
                results['max_time_ms'] = max(results['max_time_ms'], lookup_time_ms)
                
                if result['success']:
                    results['successful_lookups'] += 1
                else:
                    results['failed_lookups'] += 1
    
    total_time_s = time.time() - start_time
    
    if results['total_lookups'] > 0:
        results['avg_time_ms'] = results['total_time_ms'] / results['total_lookups']
        results['lookups_per_second'] = results['total_lookups'] / total_time_s
    
    return results


def analyze_cache_performance() -> dict[str, Any]:
    """
    Analysiert Cache-Performance des Systems.
    
    Returns:
        Cache-Analyse-Ergebnisse
    """
    monitor = get_global_monitor()
    
    analysis = {
        'caches': {},
        'overall_hit_rate': 0.0,
        'total_memory_mb': 0.0,
        'recommendations': []
    }
    
    total_hits = 0
    total_requests = 0
    
    for cache_name, metrics in monitor.caches.items():
        cache_info = {
            'hit_rate': metrics.hit_rate,
            'total_requests': metrics.total_requests,
            'entry_count': metrics.entry_count,
            'memory_mb': metrics.memory_usage_bytes / (1024 * 1024),
            'avg_lookup_ms': metrics.avg_lookup_time_ms
        }
        
        analysis['caches'][cache_name] = cache_info
        
        total_hits += metrics.hit_count
        total_requests += metrics.total_requests
        analysis['total_memory_mb'] += cache_info['memory_mb']
    
    if total_requests > 0:
        if total_requests != 0:
            analysis['overall_hit_rate'] = (total_hits / total_requests) * 100
        else:
            analysis['overall_hit_rate'] = 0.0
    
    # Generiere Empfehlungen
    analysis['recommendations'] = monitor.get_optimization_recommendations()
    
    return analysis


def get_memory_usage() -> dict[str, Any]:
    """
    Ermittelt Speicherverbrauch des Preismatrix-Systems.
    
    Returns:
        Speicher-Informationen
    """
    import gc
    
    # Trigger Garbage Collection
    gc.collect()
    
    memory_info = {
        'process_memory_mb': 0.0,
        'matrix_cache_mb': 0.0,
        'total_objects': len(gc.get_objects())
    }
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info['process_memory_mb'] = process.memory_info().rss / (1024 * 1024)
    except ImportError:
        pass
    
    # Schätze Matrix-Cache Größe
    try:
        import price_matrix_store
        
        # Hole alle Matrizen
        matrices = price_matrix_store.list_matrices()
        
        estimated_size = 0
        for matrix_info in matrices:
            matrix_data = price_matrix_store.get_matrix_full(matrix_info['id'])
            if matrix_data:
                # Schätze Größe basierend auf Zeilen/Spalten/Zellen
                rows = len(matrix_data.get('rows', []))
                cols = len(matrix_data.get('columns', []))
                cells = len(matrix_data.get('cells', {}))
                
                # Grobe Schätzung: 100 Bytes pro Zelle
                estimated_size += cells * 100
        
        memory_info['matrix_cache_mb'] = estimated_size / (1024 * 1024)
    except Exception:
        pass
    
    return memory_info


__all__ = [
    'PerformanceMonitor',
    'OperationMetrics',
    'CacheMetrics',
    'performance_tracked',
    'get_global_monitor',
    'reset_global_monitor',
    'benchmark_matrix_lookup',
    'analyze_cache_performance',
    'get_memory_usage'
]
