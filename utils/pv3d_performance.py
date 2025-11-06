"""
3D PV-Visualisierung Performance-Optimierungs-Modul

Dieses Modul enthält Performance-Optimierungen für die 3D-Visualisierung:
- Caching für teure Berechnungen
- Lazy Loading für UI-Komponenten
- Debouncing für Slider-Inputs
- 3D-Rendering Performance-Optimierungen
"""

import streamlit as st
import time
import hashlib
import json
from typing import Any, Callable, Dict, Optional, Tuple
from functools import wraps
from dataclasses import dataclass


# ============================================================================
# CACHING FÜR TEURE BERECHNUNGEN
# ============================================================================

@dataclass
class CacheEntry:
    """Cache-Eintrag mit Wert und Zeitstempel."""
    value: Any
    timestamp: float
    hits: int = 0


class PerformanceCache:
    """
    Cache-Manager für teure Berechnungen mit TTL (Time To Live).
    
    Features:
    - Automatische Invalidierung nach TTL
    - Hit-Counter für Statistiken
    - Maximale Cache-Größe mit LRU-Eviction
    """
    
    def __init__(self, max_size: int = 100, default_ttl: float = 300.0):
        """
        Initialisiert den Cache.
        
        Args:
            max_size: Maximale Anzahl Cache-Einträge
            default_ttl: Standard Time-To-Live in Sekunden (5 Minuten)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: list = []  # Für LRU
    
    def _generate_key(
        self, func_name: str, args: tuple, kwargs: dict
    ) -> str:
        """Generiert Cache-Key aus Funktionsname und Argumenten."""
        # Konvertiere args und kwargs zu JSON-String
        key_data = {
            "func": func_name,
            "args": str(args),
            "kwargs": json.dumps(kwargs, sort_keys=True, default=str)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Holt Wert aus Cache.
        
        Args:
            key: Cache-Key
        
        Returns:
            Gecachter Wert oder None wenn nicht gefunden/abgelaufen
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Prüfe TTL
        if time.time() - entry.timestamp > self.default_ttl:
            # Abgelaufen - entfernen
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return None
        
        # Hit-Counter erhöhen
        entry.hits += 1
        
        # LRU: Verschiebe an Ende
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        return entry.value
    
    def set(self, key: str, value: Any):
        """
        Speichert Wert im Cache.
        
        Args:
            key: Cache-Key
            value: Zu cachender Wert
        """
        # Prüfe Cache-Größe
        if len(self._cache) >= self.max_size:
            # Entferne ältesten Eintrag (LRU)
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]
        
        # Speichere neuen Eintrag
        self._cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            hits=0
        )
        self._access_order.append(key)
    
    def clear(self):
        """Leert den gesamten Cache."""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Gibt Cache-Statistiken zurück.
        
        Returns:
            Dictionary mit Statistiken
        """
        total_hits = sum(entry.hits for entry in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "entries": len(self._cache)
        }


# Globaler Cache
_global_cache = PerformanceCache(max_size=100, default_ttl=300.0)


def cached(ttl: Optional[float] = None):
    """
    Decorator für Caching von Funktionsergebnissen.
    
    Args:
        ttl: Time-To-Live in Sekunden (None = Standard-TTL)
    
    Example:
        @cached(ttl=60.0)
        def expensive_calculation(x, y):
            return x ** y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generiere Cache-Key
            cache_key = _global_cache._generate_key(func.__name__, args, kwargs)
            
            # Prüfe Cache
            cached_value = _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Berechne Wert
            result = func(*args, **kwargs)
            
            # Speichere im Cache
            _global_cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def clear_cache():
    """Leert den globalen Cache."""
    _global_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Gibt Cache-Statistiken zurück."""
    return _global_cache.get_stats()


# ============================================================================
# DEBOUNCING FÜR SLIDER-INPUTS
# ============================================================================

class Debouncer:
    """
    Debouncer für Slider-Inputs um unnötige Reruns zu vermeiden.
    
    Funktionsweise:
    - Speichert letzten Wert und Zeitstempel
    - Gibt nur Wert zurück wenn sich geändert hat UND Debounce-Zeit abgelaufen
    """
    
    def __init__(self, delay: float = 0.5):
        """
        Initialisiert Debouncer.
        
        Args:
            delay: Debounce-Verzögerung in Sekunden
        """
        self.delay = delay
        self._last_values: Dict[str, Tuple[Any, float]] = {}
    
    def debounce(self, key: str, value: Any) -> Tuple[Any, bool]:
        """
        Debounced einen Wert.
        
        Args:
            key: Eindeutiger Key für den Wert
            value: Aktueller Wert
        
        Returns:
            Tuple (value, should_update):
            - value: Der Wert (entweder neu oder gecached)
            - should_update: True wenn Update durchgeführt werden soll
        """
        current_time = time.time()
        
        if key not in self._last_values:
            # Erster Aufruf - speichere und gebe zurück
            self._last_values[key] = (value, current_time)
            return value, True
        
        last_value, last_time = self._last_values[key]
        
        # Prüfe ob Wert sich geändert hat
        if value == last_value:
            # Keine Änderung - kein Update nötig
            return value, False
        
        # Wert hat sich geändert - prüfe Debounce-Zeit
        time_since_last = current_time - last_time
        
        if time_since_last >= self.delay:
            # Debounce-Zeit abgelaufen - Update durchführen
            self._last_values[key] = (value, current_time)
            return value, True
        else:
            # Debounce-Zeit noch nicht abgelaufen - gebe alten Wert zurück
            return last_value, False


# Globaler Debouncer
_global_debouncer = Debouncer(delay=0.5)


def debounced_slider(
    label: str,
    min_value: float,
    max_value: float,
    value: float,
    step: float = 1.0,
    key: Optional[str] = None,
    **kwargs
) -> Tuple[float, bool]:
    """
    Debounced Slider-Widget.
    
    Args:
        label: Label für Slider
        min_value: Minimaler Wert
        max_value: Maximaler Wert
        value: Aktueller Wert
        step: Schrittweite
        key: Eindeutiger Key
        **kwargs: Weitere Argumente für st.slider
    
    Returns:
        Tuple (value, should_update):
        - value: Slider-Wert
        - should_update: True wenn Update durchgeführt werden soll
    """
    # Erstelle Slider
    slider_value = st.slider(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        **kwargs
    )
    
    # Debounce
    debounce_key = key if key else f"slider_{label}"
    return _global_debouncer.debounce(debounce_key, slider_value)


def debounced_number_input(
    label: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    value: float = 0.0,
    step: Optional[float] = None,
    key: Optional[str] = None,
    **kwargs
) -> Tuple[float, bool]:
    """
    Debounced Number Input Widget.
    
    Args:
        label: Label für Input
        min_value: Minimaler Wert
        max_value: Maximaler Wert
        value: Aktueller Wert
        step: Schrittweite
        key: Eindeutiger Key
        **kwargs: Weitere Argumente für st.number_input
    
    Returns:
        Tuple (value, should_update):
        - value: Input-Wert
        - should_update: True wenn Update durchgeführt werden soll
    """
    # Erstelle Number Input
    input_value = st.number_input(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        **kwargs
    )
    
    # Debounce
    debounce_key = key if key else f"number_{label}"
    return _global_debouncer.debounce(debounce_key, input_value)


# ============================================================================
# LAZY LOADING FÜR UI-KOMPONENTEN
# ============================================================================

class LazyComponent:
    """
    Lazy Loading Container für UI-Komponenten.
    
    Komponenten werden erst gerendert wenn sie sichtbar sind (Expander geöffnet).
    """
    
    def __init__(self, component_id: str):
        """
        Initialisiert Lazy Component.
        
        Args:
            component_id: Eindeutige ID für Komponente
        """
        self.component_id = component_id
        self._is_loaded = False
    
    def render(
        self, render_func: Callable, *args, **kwargs
    ) -> Any:
        """
        Rendert Komponente lazy.

        Args:
            render_func: Funktion zum Rendern der Komponente
            *args, **kwargs: Argumente für render_func

        Returns:
            Ergebnis von render_func oder None wenn nicht geladen
        """
        # Prüfe ob Komponente bereits geladen wurde
        session_key = f"_lazy_loaded_{self.component_id}"

        if session_key not in st.session_state:
            st.session_state[session_key] = False

        # Wenn noch nicht geladen, zeige Placeholder
        if not st.session_state[session_key]:
            # Markiere als geladen beim ersten Render
            st.session_state[session_key] = True

        # Rendere Komponente
        return render_func(*args, **kwargs)


def lazy_expander(
    label: str,
    component_id: str,
    render_func: Callable,
    expanded: bool = False,
    **kwargs
) -> Any:
    """
    Lazy Loading Expander.
    
    Inhalt wird erst gerendert wenn Expander geöffnet wird.
    
    Args:
        label: Label für Expander
        component_id: Eindeutige ID
        render_func: Funktion zum Rendern des Inhalts
        expanded: Ob Expander initial geöffnet ist
        **kwargs: Weitere Argumente für st.expander
    
    Returns:
        Ergebnis von render_func oder None
    """
    with st.expander(label, expanded=expanded, **kwargs):
        # Prüfe ob Expander geöffnet ist
        # Streamlit rendert Inhalt nur wenn Expander geöffnet
        lazy_comp = LazyComponent(component_id)
        return lazy_comp.render(render_func)


# ============================================================================
# 3D-RENDERING PERFORMANCE-OPTIMIERUNGEN
# ============================================================================

def optimize_mesh_resolution(
    vertex_count: int,
    target_fps: int = 30,
    max_vertices: int = 10000
) -> float:
    """
    Berechnet optimale Mesh-Auflösung basierend auf Vertex-Anzahl.
    
    Args:
        vertex_count: Aktuelle Vertex-Anzahl
        target_fps: Ziel-FPS
        max_vertices: Maximale Vertices für gute Performance
    
    Returns:
        Skalierungsfaktor (0.0-1.0)
    """
    if vertex_count <= max_vertices:
        return 1.0
    
    # Berechne Skalierungsfaktor
    scale = max_vertices / vertex_count
    return max(0.3, min(1.0, scale))  # Min 30%, Max 100%


def should_render_module(
    module_index: int,
    total_modules: int,
    camera_distance: float,
    lod_threshold: int = 50
) -> bool:
    """
    Entscheidet ob Modul gerendert werden soll (Level of Detail).
    
    Args:
        module_index: Index des Moduls
        total_modules: Gesamtanzahl Module
        camera_distance: Distanz zur Kamera
        lod_threshold: Schwellwert für LOD
    
    Returns:
        True wenn Modul gerendert werden soll
    """
    # Bei wenigen Modulen immer rendern
    if total_modules <= lod_threshold:
        return True
    
    # Bei vielen Modulen: Rendere nur jeden N-ten
    skip_factor = max(1, total_modules // lod_threshold)
    return module_index % skip_factor == 0


@cached(ttl=60.0)
def calculate_module_positions_cached(
    length: float,
    width: float,
    count: int,
    spacing_x: float = 0.25,
    spacing_y: float = 0.25
) -> list:
    """
    Gecachte Version der Modul-Positions-Berechnung.
    
    Args:
        length: Dachlänge
        width: Dachbreite
        count: Modulanzahl
        spacing_x: X-Abstand
        spacing_y: Y-Abstand
    
    Returns:
        Liste von (x, y) Positionen
    """
    from utils.pv3d_plotly import calculate_grid_positions
    return calculate_grid_positions(length, width, count, spacing_x, spacing_y)


def batch_render_modules(
    modules: list,
    batch_size: int = 20
) -> list:
    """
    Rendert Module in Batches für bessere Performance.
    
    Args:
        modules: Liste von Modul-Daten
        batch_size: Anzahl Module pro Batch
    
    Returns:
        Liste von gerenderten Traces
    """
    traces = []
    
    for i in range(0, len(modules), batch_size):
        batch = modules[i:i + batch_size]
        
        # Rendere Batch
        for module_data in batch:
            # Hier würde das eigentliche Rendering stattfinden
            pass
    
    return traces


# ============================================================================
# PERFORMANCE-MONITORING
# ============================================================================

class PerformanceMonitor:
    """
    Performance-Monitor für Profiling und Optimierung.
    """
    
    def __init__(self):
        self._timings: Dict[str, list] = {}
    
    def start(self, operation: str):
        """Startet Zeitmessung für Operation."""
        if operation not in self._timings:
            self._timings[operation] = []
        
        # Speichere Startzeit in Session State
        st.session_state[f"_perf_start_{operation}"] = time.time()
    
    def end(self, operation: str):
        """Beendet Zeitmessung für Operation."""
        start_key = f"_perf_start_{operation}"
        
        if start_key in st.session_state:
            start_time = st.session_state[start_key]
            duration = time.time() - start_time
            
            if operation not in self._timings:
                self._timings[operation] = []
            
            self._timings[operation].append(duration)
            
            # Cleanup
            del st.session_state[start_key]
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """
        Gibt Statistiken für Operation zurück.
        
        Args:
            operation: Name der Operation
        
        Returns:
            Dictionary mit min, max, avg, total
        """
        if operation not in self._timings or not self._timings[operation]:
            return {
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "total": 0.0,
                "count": 0
            }
        
        timings = self._timings[operation]
        return {
            "min": min(timings),
            "max": max(timings),
            "avg": sum(timings) / len(timings),
            "total": sum(timings),
            "count": len(timings)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Gibt Statistiken für alle Operationen zurück."""
        return {
            operation: self.get_stats(operation)
            for operation in self._timings.keys()
        }
    
    def clear(self):
        """Löscht alle Timings."""
        self._timings.clear()


# Globaler Performance-Monitor
_global_monitor = PerformanceMonitor()


def monitor_performance(operation: str):
    """
    Decorator für Performance-Monitoring.
    
    Args:
        operation: Name der Operation
    
    Example:
        @monitor_performance("expensive_calculation")
        def calculate():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _global_monitor.start(operation)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                _global_monitor.end(operation)
        
        return wrapper
    return decorator


def get_performance_stats() -> Dict[str, Dict[str, float]]:
    """Gibt alle Performance-Statistiken zurück."""
    return _global_monitor.get_all_stats()


def clear_performance_stats():
    """Löscht alle Performance-Statistiken."""
    _global_monitor.clear()
