# Performance-Optimierung Quick Reference

Schnellreferenz für Performance-Optimierung im shadcn/ui Theme-System.

## Quick Start

```python
from theming.theme_manager import ThemeManager
from theming.performance_optimizer import get_optimizer

# Theme Manager mit Optimierung
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')

# CSS mit Caching und Minification
css = theme_manager.generate_css(minified=True, use_cache=True)
```

## Häufige Aufgaben

### CSS generieren (optimiert)

```python
# Standard (empfohlen)
css = theme_manager.generate_css()

# Ohne Minification
css = theme_manager.generate_css(minified=False)

# Ohne Cache
css = theme_manager.generate_css(use_cache=False)
```

### Cache verwalten

```python
optimizer = get_optimizer()

# Cache-Statistiken
stats = optimizer.cache.get_stats()

# Cache invalidieren
optimizer.invalidate_cache()  # Alle
optimizer.invalidate_cache('theme-name')  # Spezifisch
```

### Metriken abrufen

```python
# Alle Metriken
metrics = optimizer.get_metrics()

# Performance-Report
report = optimizer.get_performance_report()
print(report)

# Metriken zurücksetzen
optimizer.reset_metrics()
```

### Component-Rendering messen

```python
from theming.performance_optimizer import ComponentRenderOptimizer

comp_optimizer = ComponentRenderOptimizer()

# Zeit messen
with comp_optimizer.measure_render_time('Card'):
    card.render(...)

# Statistiken
stats = comp_optimizer.get_render_stats()

# Langsame Komponenten
slow = comp_optimizer.get_slow_components(threshold_ms=50.0)
```

## Performance-Ziele

| Metrik | Ziel | Prüfen mit |
|--------|------|------------|
| CSS-Generierung | < 100ms | `metrics['css_generation_time_ms']` |
| Component-Rendering | < 50ms | `comp_optimizer.get_slow_components()` |
| CSS-Größe | < 50KB | `metrics['css_minified_size_bytes']` |
| Cache-Hit-Rate | > 80% | `metrics['cache_stats']['hit_rate']` |

## Wichtige Funktionen

### PerformanceOptimizer

```python
optimizer = get_optimizer()

# CSS generieren (optimiert)
css = optimizer.generate_optimized_css(
    theme_name='shadcn-default',
    theme_data=theme_data,
    css_generator_func=lambda: generate_css(),
    minified=True
)

# Metriken
metrics = optimizer.get_metrics()
report = optimizer.get_performance_report()

# Cache
optimizer.invalidate_cache()
optimizer.reset_metrics()
```

### CSSMinifier

```python
from theming.performance_optimizer import CSSMinifier

minifier = CSSMinifier()

# Minifizieren
minified = minifier.minify(css)

# Einsparungen
savings = minifier.calculate_savings(original, minified)
print(f"Einsparung: {savings['savings_percent']:.1f}%")
```

### ComponentRenderOptimizer

```python
comp_optimizer = ComponentRenderOptimizer()

# Zeit messen
with comp_optimizer.measure_render_time('ComponentName'):
    component.render()

# Statistiken
stats = comp_optimizer.get_render_stats()
slow = comp_optimizer.get_slow_components(threshold_ms=50.0)

# Reset
comp_optimizer.reset_stats()
```

## Metriken-Struktur

```python
{
    'css_generation_time_ms': 45.23,
    'css_size_bytes': 45678,
    'css_minified_size_bytes': 28901,
    'cache_hits': 15,
    'cache_misses': 3,
    'total_requests': 18,
    'cache_hit_rate': 83.33,
    'compression_ratio': 36.7,
    'timestamp': '2024-01-15T10:30:00',
    'cache_stats': {
        'hits': 15,
        'misses': 3,
        'total_requests': 18,
        'hit_rate': 83.33,
        'cached_items': 5,
        'max_size': 50
    }
}
```

## Best Practices

### ✅ Empfohlen

```python
# Caching aktivieren
css = theme_manager.generate_css(use_cache=True)

# Minification in Produktion
css = theme_manager.generate_css(minified=True)

# Metriken überwachen
metrics = optimizer.get_metrics()
if metrics['css_generation_time_ms'] > 100:
    print("⚠️ Performance-Problem!")

# Component-Rendering tracken
with comp_optimizer.measure_render_time('Card'):
    card.render()
```

### ❌ Vermeiden

```python
# Cache deaktivieren ohne Grund
css = theme_manager.generate_css(use_cache=False)

# Minification deaktivieren in Produktion
css = theme_manager.generate_css(minified=False)

# Metriken ignorieren
# Keine Performance-Überwachung

# Cache nie invalidieren
# Cache kann veraltet sein
```

## Troubleshooting

### CSS-Generierung langsam (> 100ms)

```python
# 1. Cache aktivieren
css = theme_manager.generate_css(use_cache=True)

# 2. Cache-Hit-Rate prüfen
stats = optimizer.cache.get_stats()
print(f"Hit-Rate: {stats['hit_rate']:.1f}%")

# 3. Bei niedriger Hit-Rate: Theme-Daten stabilisieren
```

### Komponenten langsam (> 50ms)

```python
# 1. Langsame Komponenten identifizieren
slow = comp_optimizer.get_slow_components(threshold_ms=50.0)

# 2. Render-Logik optimieren
# 3. st.cache_data verwenden
# 4. DOM-Manipulationen reduzieren
```

### Hoher Speicherverbrauch

```python
# Cache-Größe reduzieren
optimizer.cache._max_size = 10

# Cache regelmäßig leeren
optimizer.invalidate_cache()
```

## Cheat Sheet

| Aufgabe | Code |
|---------|------|
| CSS generieren | `theme_manager.generate_css()` |
| Cache-Stats | `optimizer.cache.get_stats()` |
| Cache leeren | `optimizer.invalidate_cache()` |
| Metriken | `optimizer.get_metrics()` |
| Report | `optimizer.get_performance_report()` |
| Render messen | `with comp_optimizer.measure_render_time('Name'):` |
| Langsame Komponenten | `comp_optimizer.get_slow_components()` |
| Reset | `optimizer.reset_metrics()` |

## Beispiel-Workflow

```python
# 1. Setup
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')
optimizer = get_optimizer()
comp_optimizer = ComponentRenderOptimizer()

# 2. CSS generieren (optimiert)
css = theme_manager.generate_css(minified=True, use_cache=True)

# 3. Komponenten rendern (mit Tracking)
with comp_optimizer.measure_render_time('Card'):
    card.render(title="Test", content="Content")

# 4. Performance prüfen
metrics = optimizer.get_metrics()
print(f"CSS: {metrics['css_generation_time_ms']:.2f}ms")
print(f"Cache: {metrics['cache_stats']['hit_rate']:.1f}%")

slow = comp_optimizer.get_slow_components()
if slow:
    print("Langsame Komponenten:", slow)

# 5. Bei Bedarf optimieren
if metrics['css_generation_time_ms'] > 100:
    # Cache-Strategie anpassen
    pass

if slow:
    # Komponenten optimieren
    pass
```

## Weitere Ressourcen

- [Vollständiger Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [Demo-Anwendung](../demo_performance_optimization.py)
- [Tests](../tests/test_performance_optimization.py)
