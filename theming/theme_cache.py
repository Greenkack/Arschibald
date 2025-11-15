"""
Theme Cache System

Dediziertes Caching-System für Theme-Daten und generiertes CSS.
Integriert mit Streamlit's @st.cache_data für optimale Performance.
"""

import streamlit as st
import json
import hashlib
import time
from typing import Dict, Optional, Any, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CacheStatistics:
    """Statistiken für Cache-Performance"""
    theme_cache_hits: int = 0
    theme_cache_misses: int = 0
    css_cache_hits: int = 0
    css_cache_misses: int = 0
    total_theme_loads: int = 0
    total_css_generations: int = 0
    cache_size_bytes: int = 0
    last_invalidation: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def theme_hit_rate(self) -> float:
        """Berechnet Theme-Cache-Hit-Rate in Prozent"""
        total = self.theme_cache_hits + self.theme_cache_misses
        if total == 0:
            return 0.0
        return (self.theme_cache_hits / total) * 100
    
    @property
    def css_hit_rate(self) -> float:
        """Berechnet CSS-Cache-Hit-Rate in Prozent"""
        total = self.css_cache_hits + self.css_cache_misses
        if total == 0:
            return 0.0
        return (self.css_cache_hits / total) * 100
    
    @property
    def overall_hit_rate(self) -> float:
        """Berechnet Gesamt-Hit-Rate"""
        total_hits = self.theme_cache_hits + self.css_cache_hits
        total_requests = (self.theme_cache_hits + self.theme_cache_misses + 
                         self.css_cache_hits + self.css_cache_misses)
        if total_requests == 0:
            return 0.0
        return (total_hits / total_requests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'theme_cache_hits': self.theme_cache_hits,
            'theme_cache_misses': self.theme_cache_misses,
            'css_cache_hits': self.css_cache_hits,
            'css_cache_misses': self.css_cache_misses,
            'total_theme_loads': self.total_theme_loads,
            'total_css_generations': self.total_css_generations,
            'theme_hit_rate': round(self.theme_hit_rate, 2),
            'css_hit_rate': round(self.css_hit_rate, 2),
            'overall_hit_rate': round(self.overall_hit_rate, 2),
            'cache_size_bytes': self.cache_size_bytes,
            'last_invalidation': self.last_invalidation,
            'created_at': self.created_at
        }


class ThemeCache:
    """
    Zentrales Caching-System für Themes und CSS.
    
    Verwendet Streamlit's Session State für In-Memory-Caching
    und integriert mit @st.cache_data für persistentes Caching.
    """
    
    def __init__(self, session_state=None):
        """
        Initialisiert ThemeCache
        
        Args:
            session_state: Optional session state dict (für Tests)
        """
        self._session_state = session_state if session_state is not None else st.session_state
        self._init_session_state()
    
    def _init_session_state(self) -> None:
        """Initialisiert Session State für Cache"""
        if 'theme_cache' not in self._session_state:
            self._session_state['theme_cache'] = {
                'themes': {},  # theme_name -> theme_data
                'css': {},     # cache_key -> (css, minified_css)
                'stats': CacheStatistics(),
                'theme_hashes': {},  # theme_name -> hash
            }
    
    def _generate_cache_key(self, theme_name: str, theme_data: Dict) -> str:
        """
        Generiert eindeutigen Cache-Key aus Theme-Daten
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten als Dictionary
            
        Returns:
            MD5-Hash als Cache-Key
        """
        theme_str = f"{theme_name}:{json.dumps(theme_data, sort_keys=True)}"
        return hashlib.md5(theme_str.encode()).hexdigest()
    
    def cache_theme(self, theme_name: str, theme_data: Dict) -> None:
        """
        Cached Theme-Daten im Session State
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten als Dictionary
        """
        cache = self._session_state['theme_cache']
        cache['themes'][theme_name] = theme_data
        cache['theme_hashes'][theme_name] = self._generate_cache_key(theme_name, theme_data)
        cache['stats'].total_theme_loads += 1
        
        # Update cache size
        self._update_cache_size()
    
    def get_cached_theme(self, theme_name: str) -> Optional[Dict]:
        """
        Holt Theme aus Cache
        
        Args:
            theme_name: Name des Themes
            
        Returns:
            Theme-Daten oder None wenn nicht gecached
        """
        cache = self._session_state['theme_cache']
        
        if theme_name in cache['themes']:
            cache['stats'].theme_cache_hits += 1
            return cache['themes'][theme_name]
        
        cache['stats'].theme_cache_misses += 1
        return None
    
    def cache_css(
        self,
        theme_name: str,
        theme_data: Dict,
        css: str,
        minified_css: str
    ) -> None:
        """
        Cached generiertes CSS
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten
            css: Normales CSS
            minified_css: Minifiziertes CSS
        """
        cache = self._session_state['theme_cache']
        cache_key = self._generate_cache_key(theme_name, theme_data)
        
        cache['css'][cache_key] = {
            'css': css,
            'minified_css': minified_css,
            'theme_name': theme_name,
            'cached_at': datetime.now().isoformat()
        }
        cache['stats'].total_css_generations += 1
        
        # Update cache size
        self._update_cache_size()
    
    def get_cached_css(
        self,
        theme_name: str,
        theme_data: Dict,
        minified: bool = True
    ) -> Optional[str]:
        """
        Holt CSS aus Cache
        
        Args:
            theme_name: Name des Themes
            theme_data: Theme-Daten
            minified: Ob minifizierte Version gewünscht ist
            
        Returns:
            Gecachtes CSS oder None
        """
        cache = self._session_state['theme_cache']
        cache_key = self._generate_cache_key(theme_name, theme_data)
        
        if cache_key in cache['css']:
            cache['stats'].css_cache_hits += 1
            cached_data = cache['css'][cache_key]
            return cached_data['minified_css'] if minified else cached_data['css']
        
        cache['stats'].css_cache_misses += 1
        return None
    
    def invalidate_theme(self, theme_name: str) -> None:
        """
        Invalidiert Cache für spezifisches Theme
        
        Args:
            theme_name: Name des zu invalidierenden Themes
        """
        cache = self._session_state['theme_cache']
        
        # Entferne Theme aus Cache
        if theme_name in cache['themes']:
            del cache['themes'][theme_name]
        
        if theme_name in cache['theme_hashes']:
            del cache['theme_hashes'][theme_name]
        
        # Entferne alle CSS-Einträge für dieses Theme
        keys_to_remove = [
            key for key, data in cache['css'].items()
            if data['theme_name'] == theme_name
        ]
        
        for key in keys_to_remove:
            del cache['css'][key]
        
        cache['stats'].last_invalidation = datetime.now().isoformat()
        
        # Update cache size
        self._update_cache_size()
    
    def invalidate_all(self) -> None:
        """Invalidiert gesamten Cache"""
        cache = self._session_state['theme_cache']
        cache['themes'].clear()
        cache['css'].clear()
        cache['theme_hashes'].clear()
        cache['stats'].last_invalidation = datetime.now().isoformat()
        cache['stats'].cache_size_bytes = 0
    
    def get_statistics(self) -> CacheStatistics:
        """
        Gibt Cache-Statistiken zurück
        
        Returns:
            CacheStatistics-Objekt
        """
        return self._session_state['theme_cache']['stats']
    
    def _update_cache_size(self) -> None:
        """Aktualisiert Cache-Größe in Bytes"""
        cache = self._session_state['theme_cache']
        
        # Berechne Größe der gecachten Themes
        themes_size = sum(
            len(json.dumps(data).encode('utf-8'))
            for data in cache['themes'].values()
        )
        
        # Berechne Größe des gecachten CSS
        css_size = sum(
            len(data['css'].encode('utf-8')) + len(data['minified_css'].encode('utf-8'))
            for data in cache['css'].values()
        )
        
        cache['stats'].cache_size_bytes = themes_size + css_size
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Gibt detaillierte Cache-Informationen zurück
        
        Returns:
            Dictionary mit Cache-Informationen
        """
        cache = self._session_state['theme_cache']
        
        return {
            'cached_themes': list(cache['themes'].keys()),
            'cached_themes_count': len(cache['themes']),
            'cached_css_count': len(cache['css']),
            'statistics': cache['stats'].to_dict(),
            'cache_size_kb': round(cache['stats'].cache_size_bytes / 1024, 2)
        }


# Streamlit Cache Decorators für Theme-Loading

@st.cache_data(ttl=3600, show_spinner=False)
def load_theme_from_file(theme_file_path: str) -> Dict:
    """
    Lädt Theme aus JSON-Datei mit Streamlit-Caching
    
    Args:
        theme_file_path: Pfad zur Theme-Datei
        
    Returns:
        Theme-Daten als Dictionary
        
    Note:
        Cached für 1 Stunde (3600 Sekunden)
    """
    with open(theme_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@st.cache_data(ttl=1800, show_spinner=False)
def load_all_themes(themes_dir: str) -> Dict[str, Dict]:
    """
    Lädt alle Themes aus Verzeichnis mit Streamlit-Caching
    
    Args:
        themes_dir: Pfad zum Themes-Verzeichnis
        
    Returns:
        Dictionary {theme_name: theme_data}
        
    Note:
        Cached für 30 Minuten (1800 Sekunden)
    """
    themes = {}
    themes_path = Path(themes_dir)
    
    if not themes_path.exists():
        return themes
    
    for theme_file in themes_path.glob("*.json"):
        try:
            theme_data = load_theme_from_file(str(theme_file))
            theme_name = theme_data.get('name', theme_file.stem)
            themes[theme_name] = theme_data
        except Exception as e:
            print(f"Warnung: Konnte Theme '{theme_file.name}' nicht laden: {e}")
            continue
    
    return themes


@st.cache_data(show_spinner=False)
def generate_css_cached(
    theme_name: str,
    theme_data_json: str,
    css_generator_func: Callable,
    minified: bool = True
) -> str:
    """
    Generiert CSS mit Streamlit-Caching
    
    Args:
        theme_name: Name des Themes
        theme_data_json: Theme-Daten als JSON-String (für Hashing)
        css_generator_func: Funktion die CSS generiert
        minified: Ob CSS minifiziert werden soll
        
    Returns:
        Generiertes CSS
        
    Note:
        Cached permanent bis Cache manuell geleert wird
    """
    # Diese Funktion wird von Streamlit gecached basierend auf den Parametern
    return css_generator_func()


class StreamlitCacheIntegration:
    """
    Integration mit Streamlit's Caching-System
    
    Bietet Wrapper-Funktionen die @st.cache_data nutzen
    """
    
    @staticmethod
    def clear_theme_cache() -> None:
        """Leert Streamlit's Theme-Cache"""
        load_theme_from_file.clear()
        load_all_themes.clear()
    
    @staticmethod
    def clear_css_cache() -> None:
        """Leert Streamlit's CSS-Cache"""
        generate_css_cached.clear()
    
    @staticmethod
    def clear_all_caches() -> None:
        """Leert alle Streamlit-Caches"""
        load_theme_from_file.clear()
        load_all_themes.clear()
        generate_css_cached.clear()
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Gibt Streamlit-Cache-Statistiken zurück
        
        Returns:
            Dictionary mit Cache-Informationen
        """
        # Streamlit bietet keine direkte API für Cache-Stats
        # Wir geben grundlegende Informationen zurück
        return {
            'theme_file_cache': 'active (TTL: 1h)',
            'all_themes_cache': 'active (TTL: 30min)',
            'css_generation_cache': 'active (permanent)',
            'note': 'Use clear_*_cache() methods to invalidate'
        }


# Globale Cache-Instanz
_global_cache = None


def get_theme_cache() -> ThemeCache:
    """
    Gibt globale ThemeCache-Instanz zurück
    
    Returns:
        ThemeCache-Instanz
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = ThemeCache()
    return _global_cache


def reset_theme_cache() -> None:
    """Setzt globalen Cache zurück"""
    global _global_cache
    if _global_cache:
        _global_cache.invalidate_all()
    _global_cache = None
    
    # Leere auch Streamlit-Caches
    StreamlitCacheIntegration.clear_all_caches()


# Convenience Functions

def cache_theme_data(theme_name: str, theme_data: Dict) -> None:
    """
    Cached Theme-Daten
    
    Args:
        theme_name: Name des Themes
        theme_data: Theme-Daten
    """
    cache = get_theme_cache()
    cache.cache_theme(theme_name, theme_data)


def get_cached_theme_data(theme_name: str) -> Optional[Dict]:
    """
    Holt gecachte Theme-Daten
    
    Args:
        theme_name: Name des Themes
        
    Returns:
        Theme-Daten oder None
    """
    cache = get_theme_cache()
    return cache.get_cached_theme(theme_name)


def cache_generated_css(
    theme_name: str,
    theme_data: Dict,
    css: str,
    minified_css: str
) -> None:
    """
    Cached generiertes CSS
    
    Args:
        theme_name: Name des Themes
        theme_data: Theme-Daten
        css: Normales CSS
        minified_css: Minifiziertes CSS
    """
    cache = get_theme_cache()
    cache.cache_css(theme_name, theme_data, css, minified_css)


def get_cached_css(
    theme_name: str,
    theme_data: Dict,
    minified: bool = True
) -> Optional[str]:
    """
    Holt gecachtes CSS
    
    Args:
        theme_name: Name des Themes
        theme_data: Theme-Daten
        minified: Ob minifizierte Version gewünscht ist
        
    Returns:
        Gecachtes CSS oder None
    """
    cache = get_theme_cache()
    return cache.get_cached_css(theme_name, theme_data, minified)


def invalidate_theme_cache(theme_name: Optional[str] = None) -> None:
    """
    Invalidiert Theme-Cache
    
    Args:
        theme_name: Spezifisches Theme oder None für alle
    """
    cache = get_theme_cache()
    
    if theme_name:
        cache.invalidate_theme(theme_name)
    else:
        cache.invalidate_all()
    
    # Leere auch Streamlit-Caches
    StreamlitCacheIntegration.clear_all_caches()


def get_cache_statistics() -> Dict[str, Any]:
    """
    Gibt Cache-Statistiken zurück
    
    Returns:
        Dictionary mit Statistiken
    """
    cache = get_theme_cache()
    stats = cache.get_statistics()
    cache_info = cache.get_cache_info()
    streamlit_stats = StreamlitCacheIntegration.get_cache_stats()
    
    return {
        'session_cache': cache_info,
        'streamlit_cache': streamlit_stats,
        'statistics': stats.to_dict()
    }
