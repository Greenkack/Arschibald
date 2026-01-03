"""
Performance Optimizer

Optimiert CSS-Generierung und Component-Rendering für maximale Performance.
Implementiert Caching, Minification und Performance-Monitoring.
"""

import time
import hashlib
import re
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class PerformanceMetrics:
    """Performance-Metriken für Monitoring"""
    css_generation_time_ms: float = 0.0
    css_size_bytes: int = 0
    css_minified_size_bytes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_requests: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def cache_hit_rate(self) -> float:
        """Berechnet Cache-Hit-Rate in Prozent"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def compression_ratio(self) -> float:
        """Berechnet Kompressionsrate"""
        if self.css_size_bytes == 0:
            return 0.0
        return (1 - self.css_minified_size_bytes / self.css_size_bytes) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'css_generation_time_ms': round(self.css_generation_time_ms, 2),
            'css_size_bytes': self.css_size_bytes,
            'css_minified_size_bytes': self.css_minified_size_bytes,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': self.total_requests,
            'cache_hit_rate': round(self.cache_hit_rate, 2),
            'compression_ratio': round(self.compression_ratio, 2),
            'timestamp': self.timestamp
        }


class CSSCache:
    """Cache für generiertes CSS"""
    
    def __init__(self, max_size: int = 50):
        """
        Initialisiert CSS-Cache
        
        Args:
            max_size: Maximale Anzahl gecachter CSS-Strings
        """
        self._cache: Dict[str, Tuple[str, str]] = {}  # theme_hash -> (css, minified_css)
        self._access_times: Dict[str, float] = {}
        self._theme_to_keys: Dict[str, list] = {}  # theme_name -> [cache_keys]
        self._max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _generate_cache_key(self, theme_name: str, theme_data: Dict) -> str:
        """
        Generiert Cache-Key aus Theme-Daten
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten als Dictionary
            
        Returns:
            MD5-Hash als Cache-Key
        """
        # Erstelle eindeutigen Hash aus Theme-Name und Daten
        theme_str = f"{theme_name}:{json.dumps(theme_data, sort_keys=True)}"
        return hashlib.md5(theme_str.encode()).hexdigest()
    
    def get(self, theme_name: str, theme_data: Dict, minified: bool = False) -> Optional[str]:
        """
        Holt CSS aus Cache
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten
            minified: Ob minifizierte Version gewünscht ist
            
        Returns:
            Gecachtes CSS oder None
        """
        cache_key = self._generate_cache_key(theme_name, theme_data)
        
        if cache_key in self._cache:
            self.hits += 1
            self._access_times[cache_key] = time.time()
            css, minified_css = self._cache[cache_key]
            return minified_css if minified else css
        
        self.misses += 1
        return None
    
    def set(self, theme_name: str, theme_data: Dict, css: str, minified_css: str) -> None:
        """
        Speichert CSS im Cache
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten
            css: Normales CSS
            minified_css: Minifiziertes CSS
        """
        cache_key = self._generate_cache_key(theme_name, theme_data)
        
        # Wenn Cache voll, entferne ältesten Eintrag (LRU)
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
            # Entferne auch aus theme_to_keys mapping
            for theme, keys in self._theme_to_keys.items():
                if oldest_key in keys:
                    keys.remove(oldest_key)
                    break
            del self._cache[oldest_key]
            del self._access_times[oldest_key]
        
        self._cache[cache_key] = (css, minified_css)
        self._access_times[cache_key] = time.time()
        
        # Tracking: Theme-Name zu Cache-Keys
        if theme_name not in self._theme_to_keys:
            self._theme_to_keys[theme_name] = []
        if cache_key not in self._theme_to_keys[theme_name]:
            self._theme_to_keys[theme_name].append(cache_key)
    
    def invalidate(self, theme_name: Optional[str] = None) -> None:
        """
        Invalidiert Cache
        
        Args:
            theme_name: Spezifisches Theme oder None für alle
        """
        if theme_name is None:
            self._cache.clear()
            self._access_times.clear()
            self._theme_to_keys.clear()
        else:
            # Entferne alle Einträge für dieses Theme
            if theme_name in self._theme_to_keys:
                keys_to_remove = self._theme_to_keys[theme_name].copy()
                
                for key in keys_to_remove:
                    if key in self._cache:
                        del self._cache[key]
                    if key in self._access_times:
                        del self._access_times[key]
                
                del self._theme_to_keys[theme_name]
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Cache-Statistiken zurück"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total,
            'hit_rate': round(hit_rate, 2),
            'cached_items': len(self._cache),
            'max_size': self._max_size
        }


class CSSMinifier:
    """Minifiziert CSS für kleinere Dateigröße"""
    
    @staticmethod
    def minify(css: str) -> str:
        """
        Minifiziert CSS-String
        
        Args:
            css: CSS-String
            
        Returns:
            Minifizierter CSS-String
        """
        # Entferne Kommentare
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Entferne mehrfache Leerzeichen
        css = re.sub(r'\s+', ' ', css)
        
        # Entferne Leerzeichen um Sonderzeichen
        css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)
        
        # Entferne Leerzeichen nach öffnender Klammer
        css = re.sub(r'\(\s+', '(', css)
        
        # Entferne Leerzeichen vor schließender Klammer
        css = re.sub(r'\s+\)', ')', css)
        
        # Entferne führende/trailing Leerzeichen
        css = css.strip()
        
        # Entferne letzte Semikolons vor }
        css = re.sub(r';\s*}', '}', css)
        
        # Entferne Leerzeilen
        css = re.sub(r'\n\s*\n', '\n', css)
        
        return css
    
    @staticmethod
    def calculate_savings(original: str, minified: str) -> Dict[str, Any]:
        """
        Berechnet Einsparungen durch Minification
        
        Args:
            original: Original-CSS
            minified: Minifiziertes CSS
            
        Returns:
            Dictionary mit Statistiken
        """
        original_size = len(original.encode('utf-8'))
        minified_size = len(minified.encode('utf-8'))
        savings = original_size - minified_size
        savings_percent = (savings / original_size * 100) if original_size > 0 else 0
        
        return {
            'original_size_bytes': original_size,
            'minified_size_bytes': minified_size,
            'savings_bytes': savings,
            'savings_percent': round(savings_percent, 2)
        }


class PerformanceOptimizer:
    """Hauptklasse für Performance-Optimierung"""
    
    def __init__(self, enable_cache: bool = True, enable_minification: bool = True):
        """
        Initialisiert Performance-Optimizer
        
        Args:
            enable_cache: Ob Caching aktiviert sein soll
            enable_minification: Ob Minification aktiviert sein soll
        """
        self.enable_cache = enable_cache
        self.enable_minification = enable_minification
        self.cache = CSSCache() if enable_cache else None
        self.minifier = CSSMinifier() if enable_minification else None
        self.metrics = PerformanceMetrics()
    
    def generate_optimized_css(
        self,
        theme_name: str,
        theme_data: Dict,
        css_generator_func,
        minified: bool = True
    ) -> str:
        """
        Generiert optimiertes CSS mit Caching und Minification
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten als Dictionary
            css_generator_func: Funktion die CSS generiert
            minified: Ob minifizierte Version zurückgegeben werden soll
            
        Returns:
            Optimiertes CSS
        """
        self.metrics.total_requests += 1
        
        # Versuche aus Cache zu laden
        if self.enable_cache and self.cache:
            cached_css = self.cache.get(theme_name, theme_data, minified=minified)
            if cached_css:
                self.metrics.cache_hits += 1
                return cached_css
            self.metrics.cache_misses += 1
        
        # CSS generieren und Zeit messen
        start_time = time.time()
        css = css_generator_func()
        generation_time = (time.time() - start_time) * 1000  # in ms
        
        self.metrics.css_generation_time_ms = generation_time
        self.metrics.css_size_bytes = len(css.encode('utf-8'))
        
        # Minifizieren wenn aktiviert
        minified_css = css
        if self.enable_minification and self.minifier:
            minified_css = self.minifier.minify(css)
            self.metrics.css_minified_size_bytes = len(minified_css.encode('utf-8'))
        else:
            self.metrics.css_minified_size_bytes = self.metrics.css_size_bytes
        
        # In Cache speichern
        if self.enable_cache and self.cache:
            self.cache.set(theme_name, theme_data, css, minified_css)
        
        return minified_css if minified else css
    
    def invalidate_cache(self, theme_name: Optional[str] = None) -> None:
        """
        Invalidiert Cache
        
        Args:
            theme_name: Spezifisches Theme oder None für alle
        """
        if self.cache:
            self.cache.invalidate(theme_name)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Gibt Performance-Metriken zurück"""
        metrics_dict = self.metrics.to_dict()
        
        if self.cache:
            metrics_dict['cache_stats'] = self.cache.get_stats()
        
        return metrics_dict
    
    def reset_metrics(self) -> None:
        """Setzt Metriken zurück"""
        self.metrics = PerformanceMetrics()
        if self.cache:
            self.cache.hits = 0
            self.cache.misses = 0
    
    def export_metrics(self, filepath: str) -> None:
        """
        Exportiert Metriken als JSON
        
        Args:
            filepath: Pfad zur Ausgabedatei
        """
        metrics = self.get_metrics()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)
    
    def get_performance_report(self) -> str:
        """
        Erstellt Performance-Report als String
        
        Returns:
            Formatierter Performance-Report
        """
        metrics = self.get_metrics()
        
        report = "=== Performance Report ===\n\n"
        report += f"CSS Generation Time: {metrics['css_generation_time_ms']:.2f}ms\n"
        report += f"CSS Size: {metrics['css_size_bytes']:,} bytes\n"
        report += f"Minified Size: {metrics['css_minified_size_bytes']:,} bytes\n"
        report += f"Compression: {metrics['compression_ratio']:.1f}%\n\n"
        
        if 'cache_stats' in metrics:
            cache = metrics['cache_stats']
            report += "Cache Statistics:\n"
            report += f"  Hits: {cache['hits']}\n"
            report += f"  Misses: {cache['misses']}\n"
            report += f"  Hit Rate: {cache['hit_rate']:.1f}%\n"
            report += f"  Cached Items: {cache['cached_items']}/{cache['max_size']}\n"
        
        return report


class ComponentRenderOptimizer:
    """Optimiert Component-Rendering"""
    
    def __init__(self):
        """Initialisiert Component-Render-Optimizer"""
        self.render_times: Dict[str, list] = {}
        self.render_cache: Dict[str, Any] = {}
    
    def measure_render_time(self, component_name: str):
        """
        Context Manager zum Messen der Render-Zeit
        
        Args:
            component_name: Name der Komponente
            
        Usage:
            with optimizer.measure_render_time('Card'):
                card.render(...)
        """
        class RenderTimer:
            def __init__(self, optimizer, name):
                self.optimizer = optimizer
                self.name = name
                self.start_time = None
            
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration_ms = (time.time() - self.start_time) * 1000
                if self.name not in self.optimizer.render_times:
                    self.optimizer.render_times[self.name] = []
                self.optimizer.render_times[self.name].append(duration_ms)
        
        return RenderTimer(self, component_name)
    
    def get_render_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Gibt Render-Statistiken zurück
        
        Returns:
            Dictionary mit Statistiken pro Komponente
        """
        stats = {}
        
        for component, times in self.render_times.items():
            if times:
                stats[component] = {
                    'count': len(times),
                    'avg_ms': sum(times) / len(times),
                    'min_ms': min(times),
                    'max_ms': max(times),
                    'total_ms': sum(times)
                }
        
        return stats
    
    def get_slow_components(self, threshold_ms: float = 50.0) -> list:
        """
        Gibt Liste langsamer Komponenten zurück
        
        Args:
            threshold_ms: Schwellwert in Millisekunden
            
        Returns:
            Liste von Komponenten die länger als threshold brauchen
        """
        stats = self.get_render_stats()
        slow = []
        
        for component, data in stats.items():
            if data['avg_ms'] > threshold_ms:
                slow.append({
                    'component': component,
                    'avg_ms': round(data['avg_ms'], 2),
                    'max_ms': round(data['max_ms'], 2)
                })
        
        return sorted(slow, key=lambda x: x['avg_ms'], reverse=True)
    
    def reset_stats(self) -> None:
        """Setzt Statistiken zurück"""
        self.render_times.clear()
        self.render_cache.clear()


# Globale Instanz für einfachen Zugriff
_global_optimizer = None


def get_optimizer() -> PerformanceOptimizer:
    """
    Gibt globale Optimizer-Instanz zurück
    
    Returns:
        PerformanceOptimizer-Instanz
    """
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = PerformanceOptimizer()
    return _global_optimizer


def reset_optimizer() -> None:
    """Setzt globalen Optimizer zurück"""
    global _global_optimizer
    _global_optimizer = None
