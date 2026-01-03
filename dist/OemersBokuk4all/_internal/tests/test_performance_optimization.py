"""
Tests für Performance-Optimierung

Testet CSS-Caching, Minification und Performance-Monitoring.
"""

import pytest
import time
from theming.performance_optimizer import (
    CSSCache,
    CSSMinifier,
    PerformanceOptimizer,
    ComponentRenderOptimizer,
    PerformanceMetrics,
    get_optimizer,
    reset_optimizer
)


class TestCSSCache:
    """Tests für CSS-Cache"""
    
    def test_cache_initialization(self):
        """Test: Cache wird korrekt initialisiert"""
        cache = CSSCache(max_size=10)
        
        assert cache._max_size == 10
        assert len(cache._cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_cache_set_and_get(self):
        """Test: CSS kann gespeichert und abgerufen werden"""
        cache = CSSCache()
        
        theme_name = "test-theme"
        theme_data = {"colors": {"primary": "#000"}}
        css = "body { color: #000; }"
        minified_css = "body{color:#000}"
        
        # Speichern
        cache.set(theme_name, theme_data, css, minified_css)
        
        # Abrufen (normal)
        result = cache.get(theme_name, theme_data, minified=False)
        assert result == css
        assert cache.hits == 1
        
        # Abrufen (minified)
        result = cache.get(theme_name, theme_data, minified=True)
        assert result == minified_css
        assert cache.hits == 2
    
    def test_cache_miss(self):
        """Test: Cache-Miss wird korrekt gezählt"""
        cache = CSSCache()
        
        result = cache.get("nonexistent", {}, minified=False)
        
        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0
    
    def test_cache_lru_eviction(self):
        """Test: LRU-Eviction funktioniert"""
        cache = CSSCache(max_size=2)
        
        # Fülle Cache
        cache.set("theme1", {"v": 1}, "css1", "min1")
        cache.set("theme2", {"v": 2}, "css2", "min2")
        
        assert len(cache._cache) == 2
        
        # Füge drittes Element hinzu (sollte ältestes entfernen)
        cache.set("theme3", {"v": 3}, "css3", "min3")
        
        assert len(cache._cache) == 2
        assert cache.get("theme1", {"v": 1}) is None  # Wurde entfernt
        assert cache.get("theme3", {"v": 3}) is not None  # Ist vorhanden
    
    def test_cache_invalidation(self):
        """Test: Cache-Invalidierung funktioniert"""
        cache = CSSCache()
        
        cache.set("theme1", {"v": 1}, "css1", "min1")
        cache.set("theme2", {"v": 2}, "css2", "min2")
        
        # Invalidiere alles
        cache.invalidate()
        
        assert len(cache._cache) == 0
        assert cache.get("theme1", {"v": 1}) is None
    
    def test_cache_stats(self):
        """Test: Cache-Statistiken sind korrekt"""
        cache = CSSCache()
        
        cache.set("theme1", {"v": 1}, "css1", "min1")
        cache.get("theme1", {"v": 1})  # Hit
        cache.get("theme2", {"v": 2})  # Miss
        
        stats = cache.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['total_requests'] == 2
        assert stats['hit_rate'] == 50.0
        assert stats['cached_items'] == 1


class TestCSSMinifier:
    """Tests für CSS-Minifier"""
    
    def test_minify_removes_comments(self):
        """Test: Kommentare werden entfernt"""
        css = "/* Comment */ body { color: red; }"
        minified = CSSMinifier.minify(css)
        
        assert "/*" not in minified
        assert "*/" not in minified
        assert "body" in minified
    
    def test_minify_removes_whitespace(self):
        """Test: Whitespace wird entfernt"""
        css = """
        body {
            color: red;
            margin: 0;
        }
        """
        minified = CSSMinifier.minify(css)
        
        assert "\n" not in minified or minified.count("\n") < css.count("\n")
        assert len(minified) < len(css)
    
    def test_minify_preserves_functionality(self):
        """Test: Funktionalität bleibt erhalten"""
        css = "body { color: red; margin: 0; }"
        minified = CSSMinifier.minify(css)
        
        assert "body" in minified
        assert "color" in minified
        assert "red" in minified
        assert "margin" in minified
    
    def test_calculate_savings(self):
        """Test: Einsparungen werden korrekt berechnet"""
        original = "body { color: red; }"
        minified = "body{color:red}"
        
        savings = CSSMinifier.calculate_savings(original, minified)
        
        assert savings['original_size_bytes'] > savings['minified_size_bytes']
        assert savings['savings_bytes'] > 0
        assert 0 < savings['savings_percent'] < 100
    
    def test_minify_complex_css(self):
        """Test: Komplexes CSS wird korrekt minifiziert"""
        css = """
        /* Main styles */
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .button:hover {
            background-color: blue;
        }
        """
        
        minified = CSSMinifier.minify(css)
        
        assert len(minified) < len(css)
        assert ".container" in minified
        assert ".button:hover" in minified


class TestPerformanceMetrics:
    """Tests für Performance-Metriken"""
    
    def test_metrics_initialization(self):
        """Test: Metriken werden korrekt initialisiert"""
        metrics = PerformanceMetrics()
        
        assert metrics.css_generation_time_ms == 0.0
        assert metrics.css_size_bytes == 0
        assert metrics.cache_hits == 0
        assert metrics.total_requests == 0
    
    def test_cache_hit_rate_calculation(self):
        """Test: Cache-Hit-Rate wird korrekt berechnet"""
        metrics = PerformanceMetrics()
        
        metrics.cache_hits = 8
        metrics.cache_misses = 2
        metrics.total_requests = 10
        
        assert metrics.cache_hit_rate == 80.0
    
    def test_compression_ratio_calculation(self):
        """Test: Kompressionsrate wird korrekt berechnet"""
        metrics = PerformanceMetrics()
        
        metrics.css_size_bytes = 1000
        metrics.css_minified_size_bytes = 600
        
        assert metrics.compression_ratio == 40.0
    
    def test_metrics_to_dict(self):
        """Test: Metriken können zu Dict konvertiert werden"""
        metrics = PerformanceMetrics()
        metrics.css_generation_time_ms = 50.5
        metrics.cache_hits = 5
        
        data = metrics.to_dict()
        
        assert isinstance(data, dict)
        assert data['css_generation_time_ms'] == 50.5
        assert data['cache_hits'] == 5
        assert 'timestamp' in data


class TestPerformanceOptimizer:
    """Tests für Performance-Optimizer"""
    
    def test_optimizer_initialization(self):
        """Test: Optimizer wird korrekt initialisiert"""
        optimizer = PerformanceOptimizer()
        
        assert optimizer.enable_cache is True
        assert optimizer.enable_minification is True
        assert optimizer.cache is not None
        assert optimizer.minifier is not None
    
    def test_optimizer_without_cache(self):
        """Test: Optimizer funktioniert ohne Cache"""
        optimizer = PerformanceOptimizer(enable_cache=False)
        
        assert optimizer.cache is None
    
    def test_generate_optimized_css(self):
        """Test: CSS wird optimiert generiert"""
        optimizer = PerformanceOptimizer()
        
        def generate_css():
            return "body { color: red; }"
        
        result = optimizer.generate_optimized_css(
            "test-theme",
            {"colors": {"primary": "#000"}},
            generate_css,
            minified=True
        )
        
        assert result is not None
        assert len(result) > 0
        assert optimizer.metrics.total_requests == 1
    
    def test_optimizer_caching(self):
        """Test: Caching funktioniert"""
        optimizer = PerformanceOptimizer()
        
        def generate_css():
            return "body { color: red; }"
        
        theme_name = "test-theme"
        theme_data = {"colors": {"primary": "#000"}}
        
        # Erste Generierung (Cache-Miss)
        result1 = optimizer.generate_optimized_css(
            theme_name, theme_data, generate_css, minified=True
        )
        
        # Zweite Generierung (Cache-Hit)
        result2 = optimizer.generate_optimized_css(
            theme_name, theme_data, generate_css, minified=True
        )
        
        assert result1 == result2
        assert optimizer.metrics.cache_hits >= 1
    
    def test_cache_invalidation(self):
        """Test: Cache-Invalidierung funktioniert"""
        optimizer = PerformanceOptimizer()
        
        def generate_css():
            return "body { color: red; }"
        
        # Generiere und cache
        optimizer.generate_optimized_css(
            "test-theme", {"v": 1}, generate_css, minified=True
        )
        
        # Invalidiere
        optimizer.invalidate_cache("test-theme")
        
        # Cache sollte leer sein
        assert len(optimizer.cache._cache) == 0
    
    def test_get_metrics(self):
        """Test: Metriken können abgerufen werden"""
        optimizer = PerformanceOptimizer()
        
        metrics = optimizer.get_metrics()
        
        assert isinstance(metrics, dict)
        assert 'css_generation_time_ms' in metrics
        assert 'cache_stats' in metrics
    
    def test_reset_metrics(self):
        """Test: Metriken können zurückgesetzt werden"""
        optimizer = PerformanceOptimizer()
        
        def generate_css():
            return "body { color: red; }"
        
        # Generiere CSS
        optimizer.generate_optimized_css(
            "test", {}, generate_css, minified=True
        )
        
        assert optimizer.metrics.total_requests > 0
        
        # Reset
        optimizer.reset_metrics()
        
        assert optimizer.metrics.total_requests == 0
    
    def test_performance_report(self):
        """Test: Performance-Report wird generiert"""
        optimizer = PerformanceOptimizer()
        
        def generate_css():
            return "body { color: red; }"
        
        optimizer.generate_optimized_css(
            "test", {}, generate_css, minified=True
        )
        
        report = optimizer.get_performance_report()
        
        assert isinstance(report, str)
        assert "Performance Report" in report
        assert "CSS Generation Time" in report


class TestComponentRenderOptimizer:
    """Tests für Component-Render-Optimizer"""
    
    def test_render_optimizer_initialization(self):
        """Test: Render-Optimizer wird korrekt initialisiert"""
        optimizer = ComponentRenderOptimizer()
        
        assert len(optimizer.render_times) == 0
        assert len(optimizer.render_cache) == 0
    
    def test_measure_render_time(self):
        """Test: Render-Zeit wird gemessen"""
        optimizer = ComponentRenderOptimizer()
        
        with optimizer.measure_render_time('TestComponent'):
            time.sleep(0.01)  # Simuliere Rendering
        
        assert 'TestComponent' in optimizer.render_times
        assert len(optimizer.render_times['TestComponent']) == 1
        assert optimizer.render_times['TestComponent'][0] >= 10  # mindestens 10ms
    
    def test_get_render_stats(self):
        """Test: Render-Statistiken werden berechnet"""
        optimizer = ComponentRenderOptimizer()
        
        # Simuliere mehrere Renders
        for _ in range(3):
            with optimizer.measure_render_time('Card'):
                time.sleep(0.01)
        
        stats = optimizer.get_render_stats()
        
        assert 'Card' in stats
        assert stats['Card']['count'] == 3
        assert stats['Card']['avg_ms'] >= 10
        assert 'min_ms' in stats['Card']
        assert 'max_ms' in stats['Card']
    
    def test_get_slow_components(self):
        """Test: Langsame Komponenten werden identifiziert"""
        optimizer = ComponentRenderOptimizer()
        
        # Schnelle Komponente
        with optimizer.measure_render_time('FastComponent'):
            time.sleep(0.01)
        
        # Langsame Komponente
        with optimizer.measure_render_time('SlowComponent'):
            time.sleep(0.06)
        
        slow = optimizer.get_slow_components(threshold_ms=50.0)
        
        assert len(slow) == 1
        assert slow[0]['component'] == 'SlowComponent'
        assert slow[0]['avg_ms'] > 50
    
    def test_reset_stats(self):
        """Test: Statistiken können zurückgesetzt werden"""
        optimizer = ComponentRenderOptimizer()
        
        with optimizer.measure_render_time('TestComponent'):
            time.sleep(0.01)
        
        assert len(optimizer.render_times) > 0
        
        optimizer.reset_stats()
        
        assert len(optimizer.render_times) == 0
        assert len(optimizer.render_cache) == 0


class TestGlobalOptimizer:
    """Tests für globalen Optimizer"""
    
    def test_get_optimizer(self):
        """Test: Globaler Optimizer kann abgerufen werden"""
        optimizer = get_optimizer()
        
        assert optimizer is not None
        assert isinstance(optimizer, PerformanceOptimizer)
    
    def test_get_optimizer_singleton(self):
        """Test: Globaler Optimizer ist Singleton"""
        optimizer1 = get_optimizer()
        optimizer2 = get_optimizer()
        
        assert optimizer1 is optimizer2
    
    def test_reset_optimizer(self):
        """Test: Globaler Optimizer kann zurückgesetzt werden"""
        optimizer1 = get_optimizer()
        reset_optimizer()
        optimizer2 = get_optimizer()
        
        assert optimizer1 is not optimizer2


class TestPerformanceTargets:
    """Tests für Performance-Ziele"""
    
    def test_css_generation_under_100ms(self):
        """Test: CSS-Generierung unter 100ms"""
        optimizer = PerformanceOptimizer()
        
        def generate_css():
            # Simuliere CSS-Generierung
            css = ":root { "
            for i in range(100):
                css += f"--var-{i}: value{i}; "
            css += "}"
            return css
        
        start = time.time()
        optimizer.generate_optimized_css(
            "test", {}, generate_css, minified=True
        )
        duration_ms = (time.time() - start) * 1000
        
        assert duration_ms < 100, f"CSS-Generierung zu langsam: {duration_ms:.2f}ms"
    
    def test_minified_css_size_reduction(self):
        """Test: Minification reduziert Größe signifikant"""
        css = """
        /* Large CSS with comments */
        body {
            color: red;
            margin: 0;
            padding: 0;
        }
        
        .container {
            display: flex;
            justify-content: center;
        }
        """ * 10  # Wiederhole für größere Datei
        
        minified = CSSMinifier.minify(css)
        savings = CSSMinifier.calculate_savings(css, minified)
        
        assert savings['savings_percent'] > 20, "Minification spart nicht genug"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
