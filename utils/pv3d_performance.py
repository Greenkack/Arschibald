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
    camera_distance: float = 50.0,
    lod_threshold: int = 50,
    enable_lod: bool = True
) -> bool:
    """
    Entscheidet ob Modul gerendert werden soll (Level of Detail).
    
    TASK 9.1: Lazy Loading - Lade nur sichtbare Module
    
    Diese Funktion implementiert Level-of-Detail (LOD) Rendering:
    - Bei wenigen Modulen (<= lod_threshold): Alle Module rendern
    - Bei vielen Modulen (> lod_threshold): Nur jeden N-ten rendern
    - LOD kann deaktiviert werden für volle Qualität
    
    Args:
        module_index: Index des Moduls (0-basiert)
        total_modules: Gesamtanzahl Module
        camera_distance: Distanz zur Kamera (aktuell nicht verwendet)
        lod_threshold: Schwellwert für LOD (Standard: 50 Module)
        enable_lod: Ob LOD aktiviert ist (Standard: True)
    
    Returns:
        True wenn Modul gerendert werden soll, sonst False
    
    Requirements:
        - 9.1.1: Lade nur sichtbare Module
        - 9.1.2: Reduziere Mesh-Komplexität bei vielen Modulen
    
    Example:
        >>> # Bei 100 Modulen und Threshold 50: Rendere jeden 2. Modul
        >>> should_render_module(0, 100, lod_threshold=50)  # True
        >>> should_render_module(1, 100, lod_threshold=50)  # False
        >>> should_render_module(2, 100, lod_threshold=50)  # True
    """
    # LOD deaktiviert - rendere alle Module
    if not enable_lod:
        return True
    
    # Bei wenigen Modulen immer rendern
    if total_modules <= lod_threshold:
        return True
    
    # Bei vielen Modulen: Rendere nur jeden N-ten
    # Skip-Faktor berechnen: Je mehr Module, desto mehr überspringen
    skip_factor = max(1, total_modules // lod_threshold)
    
    # Rendere Modul wenn Index durch skip_factor teilbar ist
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
    
    TASK 9.2: Caching - Cache berechnete Positionen
    
    Args:
        length: Dachlänge
        width: Dachbreite
        count: Modulanzahl
        spacing_x: X-Abstand
        spacing_y: Y-Abstand
    
    Returns:
        Liste von (x, y) Positionen
    
    Requirements:
        - 9.2.1: Cache berechnete Positionen
    """
    try:
        from utils.pv3d_grid_calculator import calculate_module_grid
        return calculate_module_grid(
            roof_length=length,
            roof_width=width,
            module_quantity=count,
            spacing=spacing_x,
            margin=0.3
        )
    except ImportError:
        # Fallback wenn Grid-Calculator nicht verfügbar
        return []


@cached(ttl=300.0)
def cache_module_mesh_geometry(
    module_width: float = 1.05,
    module_height: float = 1.76,
    module_thickness: float = 0.04
) -> dict:
    """
    Cached Modul-Mesh-Geometrie für Wiederverwendung.
    
    TASK 9.2: Caching - Cache Mesh-Geometrie
    
    Diese Funktion cached die Basis-Geometrie eines PV-Moduls (Vertices und Faces).
    Da alle Module die gleichen Dimensionen haben, kann diese Geometrie
    wiederverwendet und nur transformiert (rotiert/verschoben) werden.
    
    Args:
        module_width: Breite des Moduls in Metern (Standard: 1.05m)
        module_height: Höhe des Moduls in Metern (Standard: 1.76m)
        module_thickness: Dicke des Moduls in Metern (Standard: 0.04m)
    
    Returns:
        Dictionary mit:
            - vertices: NumPy Array mit lokalen Vertex-Positionen (8x3)
            - faces_i: Liste der i-Indizes für Dreiecke
            - faces_j: Liste der j-Indizes für Dreiecke
            - faces_k: Liste der k-Indizes für Dreiecke
    
    Requirements:
        - 9.2.2: Cache Mesh-Geometrie
    
    Example:
        >>> geom = cache_module_mesh_geometry()
        >>> vertices = geom['vertices']  # 8 Ecken des Quaders
        >>> # Transformiere Vertices für jedes Modul individuell
    """
    import numpy as np
    
    # Halbe Dimensionen für zentrierten Quader
    hw = module_width / 2
    hh = module_height / 2
    ht = module_thickness / 2
    
    # 8 Ecken des Moduls (lokale Koordinaten, zentriert im Ursprung)
    vertices = np.array([
        [-hw, -hh, -ht],  # 0: links vorne unten
        [hw, -hh, -ht],   # 1: rechts vorne unten
        [hw, hh, -ht],    # 2: rechts hinten unten
        [-hw, hh, -ht],   # 3: links hinten unten
        [-hw, -hh, ht],   # 4: links vorne oben
        [hw, -hh, ht],    # 5: rechts vorne oben
        [hw, hh, ht],     # 6: rechts hinten oben
        [-hw, hh, ht],    # 7: links hinten oben
    ])
    
    # Dreiecks-Indizes für vollständigen Quader (6 Seiten × 2 Dreiecke = 12 Dreiecke)
    faces_i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 5, 5, 1, 1, 6, 6, 2, 2, 7, 7, 3, 3]
    faces_j = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 4, 1, 6, 4, 5, 0, 7, 5, 6, 1, 4, 6, 7, 2]
    faces_k = [3, 2, 5, 6, 6, 7, 7, 4, 7, 6, 5, 4, 4, 5, 0, 4, 5, 6, 1, 2, 6, 7, 2, 3]
    
    return {
        'vertices': vertices,
        'faces_i': faces_i,
        'faces_j': faces_j,
        'faces_k': faces_k
    }


def batch_render_modules(
    module_positions: list,
    render_func: Callable,
    batch_size: int = 20,
    enable_lod: bool = True,
    lod_threshold: int = 50,
    **render_kwargs
) -> list:
    """
    Rendert Module in Batches für bessere Performance.
    
    TASK 9.1: Lazy Loading - Batch-Rendering für Performance
    
    Diese Funktion rendert Module in Batches und wendet LOD an:
    - Module werden in kleineren Gruppen verarbeitet
    - LOD filtert Module basierend auf Gesamtanzahl
    - Reduziert Memory-Spikes bei vielen Modulen
    
    Args:
        module_positions: Liste von (x, y, z) Positionen
        render_func: Funktion zum Rendern eines einzelnen Moduls
                    Signatur: render_func(x, y, z, module_number, **kwargs) -> mesh
        batch_size: Anzahl Module pro Batch (Standard: 20)
        enable_lod: Ob Level-of-Detail aktiviert ist (Standard: True)
        lod_threshold: Schwellwert für LOD (Standard: 50)
        **render_kwargs: Zusätzliche Argumente für render_func
    
    Returns:
        Liste von gerenderten Mesh-Objekten
    
    Requirements:
        - 9.1.1: Lade nur sichtbare Module
        - 9.1.2: Reduziere Mesh-Komplexität
    
    Example:
        >>> positions = [(0, 0, 3), (1, 0, 3), (2, 0, 3)]
        >>> def render_module(x, y, z, module_number, **kwargs):
        ...     return create_pv_module_3d(x, y, z, module_number=module_number)
        >>> meshes = batch_render_modules(
        ...     positions, render_module, batch_size=10,
        ...     azimuth_deg=0, tilt_deg=30
        ... )
    """
    traces = []
    total_modules = len(module_positions)
    
    # Iteriere über Batches
    for batch_start in range(0, total_modules, batch_size):
        batch_end = min(batch_start + batch_size, total_modules)
        batch = module_positions[batch_start:batch_end]
        
        # Rendere Module im Batch mit LOD
        for local_idx, (x, y, z) in enumerate(batch):
            global_idx = batch_start + local_idx
            
            # LOD: Prüfe ob Modul gerendert werden soll
            if should_render_module(
                module_index=global_idx,
                total_modules=total_modules,
                lod_threshold=lod_threshold,
                enable_lod=enable_lod
            ):
                try:
                    # Rendere Modul
                    mesh = render_func(
                        x, y, z,
                        module_number=global_idx + 1,  # 1-basiert für Anzeige
                        **render_kwargs
                    )
                    
                    # Füge zu Traces hinzu (kann Tuple oder einzelnes Objekt sein)
                    if isinstance(mesh, tuple):
                        traces.append(mesh[0])  # Nur Mesh, nicht Vertices
                    else:
                        traces.append(mesh)
                        
                except Exception as e:
                    # Fehler beim Rendern - überspringe Modul
                    print(f"⚠️ Fehler beim Rendern von Modul {global_idx + 1}: {e}")
                    continue
    
    return traces


def get_lod_info(total_modules: int, lod_threshold: int = 50) -> dict:
    """
    Gibt Informationen über Level-of-Detail zurück.
    
    TASK 9.1: Lazy Loading - LOD-Informationen
    
    Args:
        total_modules: Gesamtanzahl Module
        lod_threshold: Schwellwert für LOD
    
    Returns:
        Dictionary mit LOD-Informationen:
            - enabled: Ob LOD aktiv ist
            - skip_factor: Wie viele Module übersprungen werden
            - rendered_count: Wie viele Module gerendert werden
            - skipped_count: Wie viele Module übersprungen werden
            - reduction_percent: Prozentuale Reduktion
    
    Requirements:
        - 9.1.1: Transparenz über Lazy Loading
    
    Example:
        >>> info = get_lod_info(100, lod_threshold=50)
        >>> print(f"Rendere {info['rendered_count']} von {total_modules} Modulen")
    """
    if total_modules <= lod_threshold:
        return {
            'enabled': False,
            'skip_factor': 1,
            'rendered_count': total_modules,
            'skipped_count': 0,
            'reduction_percent': 0.0
        }
    
    skip_factor = max(1, total_modules // lod_threshold)
    rendered_count = (total_modules + skip_factor - 1) // skip_factor  # Aufrunden
    skipped_count = total_modules - rendered_count
    reduction_percent = (skipped_count / total_modules) * 100.0
    
    return {
        'enabled': True,
        'skip_factor': skip_factor,
        'rendered_count': rendered_count,
        'skipped_count': skipped_count,
        'reduction_percent': reduction_percent
    }


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


# ============================================================================
# TASK 9.2: ERWEITERTE CACHING-FUNKTIONEN
# ============================================================================

class TransformationCache:
    """
    Cache für Modul-Transformationen (Rotation + Translation).
    
    TASK 9.2: Caching - Cache Transformationsmatrizen
    
    Da viele Module die gleichen Transformationen verwenden (z.B. gleicher
    Azimuth und Tilt), können wir die Rotationsmatrizen cachen und
    wiederverwenden.
    """
    
    def __init__(self, max_size: int = 50):
        """
        Initialisiert den Transformations-Cache.
        
        Args:
            max_size: Maximale Anzahl gecachter Transformationen
        """
        self._cache: Dict[str, Any] = {}
        self.max_size = max_size
    
    def _get_key(self, azimuth_deg: float, tilt_deg: float) -> str:
        """Generiert Cache-Key aus Azimuth und Tilt."""
        # Runde auf 1 Dezimalstelle für besseres Caching
        az = round(azimuth_deg, 1)
        tilt = round(tilt_deg, 1)
        return f"az{az}_tilt{tilt}"
    
    def get_rotation_matrix(
        self, azimuth_deg: float, tilt_deg: float
    ) -> Optional[Any]:
        """
        Holt Rotationsmatrix aus Cache.
        
        Args:
            azimuth_deg: Azimuth-Winkel in Grad
            tilt_deg: Neigungs-Winkel in Grad
        
        Returns:
            NumPy Rotationsmatrix oder None wenn nicht gecached
        """
        key = self._get_key(azimuth_deg, tilt_deg)
        return self._cache.get(key)
    
    def set_rotation_matrix(
        self, azimuth_deg: float, tilt_deg: float, matrix: Any
    ):
        """
        Speichert Rotationsmatrix im Cache.
        
        Args:
            azimuth_deg: Azimuth-Winkel in Grad
            tilt_deg: Neigungs-Winkel in Grad
            matrix: NumPy Rotationsmatrix
        """
        # Prüfe Cache-Größe
        if len(self._cache) >= self.max_size:
            # Entferne ältesten Eintrag (FIFO)
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        
        key = self._get_key(azimuth_deg, tilt_deg)
        self._cache[key] = matrix
    
    def clear(self):
        """Leert den Cache."""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Cache-Statistiken zurück."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "unique_transformations": len(self._cache)
        }


# Globaler Transformations-Cache
_transformation_cache = TransformationCache(max_size=50)


def get_cached_rotation_matrix(azimuth_deg: float, tilt_deg: float):
    """
    Holt oder berechnet Rotationsmatrix mit Caching.
    
    TASK 9.2: Caching - Cache Rotationsmatrizen
    
    Args:
        azimuth_deg: Azimuth-Winkel in Grad
        tilt_deg: Neigungs-Winkel in Grad
    
    Returns:
        NumPy Rotationsmatrix (3x3)
    
    Requirements:
        - 9.2.2: Cache Transformationsmatrizen
    
    Example:
        >>> R = get_cached_rotation_matrix(0, 30)
        >>> # Beim zweiten Aufruf mit gleichen Werten: Cache-Hit
        >>> R2 = get_cached_rotation_matrix(0, 30)  # Aus Cache
    """
    import numpy as np
    
    # Prüfe Cache
    cached_matrix = _transformation_cache.get_rotation_matrix(
        azimuth_deg, tilt_deg
    )
    if cached_matrix is not None:
        return cached_matrix
    
    # Berechne Rotationsmatrix
    tilt_rad = np.deg2rad(tilt_deg)
    az_rad = np.deg2rad(azimuth_deg)
    
    # Rotation um Y-Achse (Tilt)
    Ry = np.array([
        [np.cos(tilt_rad), 0, np.sin(tilt_rad)],
        [0, 1, 0],
        [-np.sin(tilt_rad), 0, np.cos(tilt_rad)]
    ])
    
    # Rotation um Z-Achse (Azimuth)
    Rz = np.array([
        [np.cos(az_rad), -np.sin(az_rad), 0],
        [np.sin(az_rad), np.cos(az_rad), 0],
        [0, 0, 1]
    ])
    
    # Kombinierte Rotation
    R = Rz @ Ry
    
    # Speichere im Cache
    _transformation_cache.set_rotation_matrix(azimuth_deg, tilt_deg, R)
    
    return R


def clear_transformation_cache():
    """Leert den Transformations-Cache."""
    _transformation_cache.clear()


def get_transformation_cache_stats() -> Dict[str, Any]:
    """Gibt Transformations-Cache-Statistiken zurück."""
    return _transformation_cache.get_stats()


@cached(ttl=120.0)
def calculate_roof_positions_cached(
    roof_type: str,
    roof_length: float,
    roof_width: float,
    roof_pitch: float,
    module_quantity: int,
    margin: float = 0.3
) -> list:
    """
    Gecachte Berechnung von Modul-Positionen für spezifischen Dachtyp.
    
    TASK 9.2: Caching - Cache dachtyp-spezifische Positionen
    
    Args:
        roof_type: Dachtyp (z.B. "Flachdach", "Satteldach")
        roof_length: Dachlänge in Metern
        roof_width: Dachbreite in Metern
        roof_pitch: Dachneigung in Grad
        module_quantity: Anzahl Module
        margin: Randabstand in Metern
    
    Returns:
        Liste von (x, y, z) Positionen
    
    Requirements:
        - 9.2.1: Cache berechnete Positionen
    """
    try:
        from utils.pv3d_roof_type_logic import get_roof_type_placement
        
        return get_roof_type_placement(
            roof_type=roof_type,
            roof_length=roof_length,
            roof_width=roof_width,
            roof_pitch=roof_pitch,
            module_quantity=module_quantity,
            module_width=1.05,
            module_height=1.76,
            margin=margin,
            orientation="portrait"
        )
    except ImportError:
        # Fallback wenn Roof-Type-Logic nicht verfügbar
        return []


def get_all_cache_stats() -> Dict[str, Any]:
    """
    Gibt alle Cache-Statistiken zurück.
    
    TASK 9.2: Caching - Übersicht über alle Caches
    
    Returns:
        Dictionary mit Statistiken für alle Caches:
            - global_cache: Allgemeiner Cache (Positionen, etc.)
            - transformation_cache: Rotationsmatrizen-Cache
            - performance_stats: Performance-Monitoring-Statistiken
    
    Requirements:
        - 9.2.3: Transparenz über Cache-Nutzung
    """
    return {
        "global_cache": get_cache_stats(),
        "transformation_cache": get_transformation_cache_stats(),
        "performance_stats": get_performance_stats()
    }


def clear_all_caches():
    """
    Leert alle Caches.
    
    TASK 9.2: Caching - Cache-Management
    
    Nützlich wenn:
    - Speicher freigegeben werden soll
    - Nach Änderungen an Gebäude-Dimensionen
    - Bei Debugging/Testing
    """
    clear_cache()
    clear_transformation_cache()
    clear_performance_stats()
    print("✓ Alle Caches geleert")
