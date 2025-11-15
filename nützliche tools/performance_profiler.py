#!/usr/bin/env python3
"""
Performance-Profiler für Python-Code
"""
import cProfile
import io
import pstats
import time

import psutil


def profile_function(func, *args, **kwargs):
    """Profiled eine spezifische Funktion"""

    profiler = cProfile.Profile()

    # Memory vor Ausführung
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB

    # Zeit messen
    start_time = time.time()

    # Profiling starten
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    # Zeit nach Ausführung
    end_time = time.time()
    execution_time = end_time - start_time

    # Memory nach Ausführung
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_diff = memory_after - memory_before

    # Profiling-Ergebnisse
    stats_stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_stream)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10

    print("PERFORMANCE-ANALYSE:")
    print(f"⏱️ Ausführungszeit: {execution_time:.4f} Sekunden")
    print(f"💾 Memory-Verbrauch: {memory_diff:.2f} MB")
    print("Top-10 langsamste Funktionen:")
    print(stats_stream.getvalue())

    return result

# Decorator-Version


def profile_performance(func):
    """Decorator für automatisches Performance-Profiling"""
    def wrapper(*args, **kwargs):
        return profile_function(func, *args, **kwargs)
    return wrapper


if __name__ == "__main__":
    # Beispiel-Verwendung:
    @profile_performance
    def test_function():
        return sum(range(1000000))

    test_function()
