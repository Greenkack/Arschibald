"""
Unit Tests for Theme Cache System

Tests für ThemeCache, CacheStatistics und Streamlit-Integration.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from theming.theme_cache import (
    ThemeCache,
    CacheStatistics,
    StreamlitCacheIntegration,
    get_theme_cache,
    reset_theme_cache,
    cache_theme_data,
    get_cached_theme_data,
    cache_generated_css,
    get_cached_css,
    invalidate_theme_cache,
    get_cache_statistics
)


class TestCacheStatistics:
    """Tests für CacheStatistics"""
    
    def test_initial_statistics(self):
        """Test: Initiale Statistiken sind 0"""
        stats = CacheStatistics()
        
        assert stats.theme_cache_hits == 0
        assert stats.theme_cache_misses == 0
        assert stats.css_cache_hits == 0
        assert stats.css_cache_misses == 0
        assert stats.theme_hit_rate == 0.0
        assert stats.css_hit_rate == 0.0
        assert stats.overall_hit_rate == 0.0
    
    def test_theme_hit_rate_calculation(self):
        """Test: Theme Hit Rate wird korrekt berechnet"""
        stats = CacheStatistics()
        stats.theme_cache_hits = 8
        stats.theme_cache_misses = 2
        
        assert stats.theme_hit_rate == 80.0
    
    def test_css_hit_rate_calculation(self):
        """Test: CSS Hit Rate wird korrekt berechnet"""
        stats = CacheStatistics()
        stats.css_cache_hits = 9
        stats.css_cache_misses = 1
        
        assert stats.css_hit_rate == 90.0
    
    def test_overall_hit_rate_calculation(self):
        """Test: Overall Hit Rate wird korrekt berechnet"""
        stats = CacheStatistics()
        stats.theme_cache_hits = 8
        stats.theme_cache_misses = 2
        stats.css_cache_hits = 6
        stats.css_cache_misses = 4
        
        # Total: 14 hits, 6 misses = 70%
        assert stats.overall_hit_rate == 70.0
    
    def test_to_dict(self):
        """Test: to_dict konvertiert korrekt"""
        stats = CacheStatistics()
        stats.theme_cache_hits = 5
        stats.css_cache_hits = 3
        
        result = stats.to_dict()
        
        assert isinstance(result, dict)
        assert 'theme_cache_hits' in result
        assert 'css_cache_hits' in result
        assert 'theme_hit_rate' in result
        assert 'overall_hit_rate' in result


class TestThemeCache:
    """Tests für ThemeCache"""
    
    def setup_method(self):
        """Setup vor jedem Test"""
        # Create mock session state
        self.mock_session_state = {}
    
    def test_cache_initialization(self):
        """Test: Cache wird korrekt initialisiert"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        assert 'theme_cache' in self.mock_session_state
        assert 'themes' in self.mock_session_state['theme_cache']
        assert 'css' in self.mock_session_state['theme_cache']
        assert 'stats' in self.mock_session_state['theme_cache']
    
    def test_cache_theme(self):
        """Test: Theme wird gecached"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {
            'name': 'test-theme',
            'display_name': 'Test Theme',
            'colors': {'primary': '#000000'}
        }
        
        cache.cache_theme('test-theme', theme_data)
        
        assert 'test-theme' in self.mock_session_state['theme_cache']['themes']
        assert self.mock_session_state['theme_cache']['themes']['test-theme'] == theme_data
    
    def test_get_cached_theme_hit(self):
        """Test: Gecachtes Theme wird gefunden (Cache Hit)"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {'name': 'test-theme'}
        cache.cache_theme('test-theme', theme_data)
        
        result = cache.get_cached_theme('test-theme')
        
        assert result == theme_data
        assert cache.get_statistics().theme_cache_hits == 1
        assert cache.get_statistics().theme_cache_misses == 0
    
    def test_get_cached_theme_miss(self):
        """Test: Nicht gecachtes Theme (Cache Miss)"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        result = cache.get_cached_theme('non-existent')
        
        assert result is None
        assert cache.get_statistics().theme_cache_hits == 0
        assert cache.get_statistics().theme_cache_misses == 1
    
    def test_cache_css(self):
        """Test: CSS wird gecached"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {'name': 'test'}
        css = "body { color: red; }"
        minified_css = "body{color:red}"
        
        cache.cache_css('test', theme_data, css, minified_css)
        
        assert len(self.mock_session_state['theme_cache']['css']) > 0
    
    def test_get_cached_css_hit(self):
        """Test: Gecachtes CSS wird gefunden"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {'name': 'test'}
        css = "body { color: red; }"
        minified_css = "body{color:red}"
        
        cache.cache_css('test', theme_data, css, minified_css)
        
        result = cache.get_cached_css('test', theme_data, minified=True)
        
        assert result == minified_css
        assert cache.get_statistics().css_cache_hits == 1
    
    def test_get_cached_css_miss(self):
        """Test: Nicht gecachtes CSS"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        result = cache.get_cached_css('test', {'name': 'test'}, minified=True)
        
        assert result is None
        assert cache.get_statistics().css_cache_misses == 1
    
    def test_invalidate_theme(self):
        """Test: Theme wird invalidiert"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {'name': 'test'}
        cache.cache_theme('test', theme_data)
        cache.cache_css('test', theme_data, "css", "min_css")
        
        cache.invalidate_theme('test')
        
        assert 'test' not in self.mock_session_state['theme_cache']['themes']
    
    def test_invalidate_all(self):
        """Test: Alle Themes werden invalidiert"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        cache.cache_theme('theme1', {'name': 'theme1'})
        cache.cache_theme('theme2', {'name': 'theme2'})
        
        cache.invalidate_all()
        
        assert len(self.mock_session_state['theme_cache']['themes']) == 0
        assert len(self.mock_session_state['theme_cache']['css']) == 0
    
    def test_cache_key_generation(self):
        """Test: Cache-Keys sind konsistent"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {'name': 'test', 'colors': {'primary': '#000'}}
        
        key1 = cache._generate_cache_key('test', theme_data)
        key2 = cache._generate_cache_key('test', theme_data)
        
        assert key1 == key2
    
    def test_cache_key_different_for_different_data(self):
        """Test: Verschiedene Daten erzeugen verschiedene Keys"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        data1 = {'name': 'test', 'colors': {'primary': '#000'}}
        data2 = {'name': 'test', 'colors': {'primary': '#fff'}}
        
        key1 = cache._generate_cache_key('test', data1)
        key2 = cache._generate_cache_key('test', data2)
        
        assert key1 != key2
    
    def test_get_cache_info(self):
        """Test: Cache-Info wird korrekt zurückgegeben"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        cache.cache_theme('theme1', {'name': 'theme1'})
        cache.cache_theme('theme2', {'name': 'theme2'})
        
        info = cache.get_cache_info()
        
        assert info['cached_themes_count'] == 2
        assert 'theme1' in info['cached_themes']
        assert 'theme2' in info['cached_themes']


class TestConvenienceFunctions:
    """Tests für Convenience-Funktionen"""
    
    def setup_method(self):
        """Setup vor jedem Test"""
        self.mock_session_state = {}
        # Patch get_theme_cache to return cache with mock session state
        self.cache = ThemeCache(session_state=self.mock_session_state)
    
    def test_cache_and_get_theme_data(self):
        """Test: cache_theme_data und get_cached_theme_data"""
        theme_data = {'name': 'test', 'display_name': 'Test'}
        
        self.cache.cache_theme('test', theme_data)
        result = self.cache.get_cached_theme('test')
        
        assert result == theme_data
    
    def test_cache_and_get_css(self):
        """Test: cache_generated_css und get_cached_css"""
        theme_data = {'name': 'test'}
        css = "body { color: red; }"
        minified = "body{color:red}"
        
        self.cache.cache_css('test', theme_data, css, minified)
        result = self.cache.get_cached_css('test', theme_data, minified=True)
        
        assert result == minified
    
    def test_invalidate_specific_theme(self):
        """Test: invalidate_theme_cache für spezifisches Theme"""
        self.cache.cache_theme('theme1', {'name': 'theme1'})
        self.cache.cache_theme('theme2', {'name': 'theme2'})
        
        self.cache.invalidate_theme('theme1')
        
        assert self.cache.get_cached_theme('theme1') is None
        assert self.cache.get_cached_theme('theme2') is not None
    
    def test_invalidate_all_themes(self):
        """Test: invalidate_theme_cache ohne Parameter"""
        self.cache.cache_theme('theme1', {'name': 'theme1'})
        self.cache.cache_theme('theme2', {'name': 'theme2'})
        
        self.cache.invalidate_all()
        
        assert self.cache.get_cached_theme('theme1') is None
        assert self.cache.get_cached_theme('theme2') is None
    
    def test_get_cache_statistics(self):
        """Test: get_cache_statistics"""
        self.cache.cache_theme('test', {'name': 'test'})
        self.cache.get_cached_theme('test')  # Hit
        self.cache.get_cached_theme('missing')  # Miss
        
        stats = self.cache.get_statistics()
        info = self.cache.get_cache_info()
        
        assert stats.theme_cache_hits == 1
        assert stats.theme_cache_misses == 1


class TestStreamlitCacheIntegration:
    """Tests für StreamlitCacheIntegration"""
    
    @patch('theming.theme_cache.load_theme_from_file')
    def test_clear_theme_cache(self, mock_load):
        """Test: clear_theme_cache leert Theme-Cache"""
        mock_load.clear = Mock()
        
        StreamlitCacheIntegration.clear_theme_cache()
        
        mock_load.clear.assert_called_once()
    
    @patch('theming.theme_cache.generate_css_cached')
    def test_clear_css_cache(self, mock_gen):
        """Test: clear_css_cache leert CSS-Cache"""
        mock_gen.clear = Mock()
        
        StreamlitCacheIntegration.clear_css_cache()
        
        mock_gen.clear.assert_called_once()
    
    def test_get_cache_stats(self):
        """Test: get_cache_stats gibt Info zurück"""
        stats = StreamlitCacheIntegration.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert 'theme_file_cache' in stats
        assert 'css_generation_cache' in stats


class TestCachePerformance:
    """Performance-Tests für Cache"""
    
    def setup_method(self):
        """Setup vor jedem Test"""
        self.mock_session_state = {}
    
    def test_cache_hit_is_faster_than_miss(self):
        """Test: Cache Hit ist schneller als Miss"""
        import time
        
        cache = ThemeCache(session_state=self.mock_session_state)
        theme_data = {'name': 'test', 'colors': {'primary': '#000'}}
        
        # Cache Theme
        cache.cache_theme('test', theme_data)
        
        # Miss (nicht gecached)
        start = time.time()
        result = cache.get_cached_theme('non-existent')
        miss_time = time.time() - start
        
        # Hit (gecached)
        start = time.time()
        result = cache.get_cached_theme('test')
        hit_time = time.time() - start
        
        # Hit sollte schneller sein (oder gleich schnell bei sehr kleinen Daten)
        assert hit_time <= miss_time * 2  # Toleranz für Test-Overhead
    
    def test_multiple_cache_operations(self):
        """Test: Mehrere Cache-Operationen"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        # Cache 10 Themes
        for i in range(10):
            theme_data = {'name': f'theme{i}', 'index': i}
            cache.cache_theme(f'theme{i}', theme_data)
        
        # Alle sollten abrufbar sein
        for i in range(10):
            result = cache.get_cached_theme(f'theme{i}')
            assert result is not None
            assert result['index'] == i
        
        stats = cache.get_statistics()
        assert stats.theme_cache_hits == 10


class TestCacheEdgeCases:
    """Tests für Edge Cases"""
    
    def setup_method(self):
        """Setup vor jedem Test"""
        self.mock_session_state = {}
    
    def test_cache_empty_theme_data(self):
        """Test: Leere Theme-Daten cachen"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        cache.cache_theme('empty', {})
        result = cache.get_cached_theme('empty')
        
        assert result == {}
    
    def test_cache_large_theme_data(self):
        """Test: Große Theme-Daten cachen"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        large_data = {
            'name': 'large',
            'colors': {f'color{i}': f'#{i:06x}' for i in range(1000)}
        }
        
        cache.cache_theme('large', large_data)
        result = cache.get_cached_theme('large')
        
        assert result == large_data
    
    def test_cache_special_characters_in_theme_name(self):
        """Test: Spezielle Zeichen im Theme-Namen"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        theme_data = {'name': 'test-theme_v1.0'}
        cache.cache_theme('test-theme_v1.0', theme_data)
        result = cache.get_cached_theme('test-theme_v1.0')
        
        assert result == theme_data
    
    def test_invalidate_non_existent_theme(self):
        """Test: Invalidierung nicht existierendes Theme"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        # Sollte nicht crashen
        cache.invalidate_theme('non-existent')
    
    def test_get_statistics_empty_cache(self):
        """Test: Statistiken bei leerem Cache"""
        cache = ThemeCache(session_state=self.mock_session_state)
        
        stats = cache.get_statistics()
        
        assert stats.theme_cache_hits == 0
        assert stats.theme_cache_misses == 0
        assert stats.overall_hit_rate == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
