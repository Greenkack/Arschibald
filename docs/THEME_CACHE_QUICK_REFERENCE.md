# Theme Cache System - Quick Reference

## Quick Start

```python
from theming.theme_cache import (
    get_theme_cache,
    cache_theme_data,
    get_cached_theme_data,
    cache_generated_css,
    get_cached_css,
    invalidate_theme_cache,
    get_cache_statistics
)

# Cache initialisieren
cache = get_theme_cache()

# Theme cachen
cache_theme_data('shadcn-default', theme_data)

# Theme abrufen
theme_data = get_cached_theme_data('shadcn-default')

# CSS cachen
cache_generated_css('shadcn-default', theme_data, css, minified_css)

# CSS abrufen
css = get_cached_css('shadcn-default', theme_data, minified=True)

# Cache invalidieren
invalidate_theme_cache('shadcn-default')  # Spezifisch
invalidate_theme_cache()  # Alle

# Statistiken
stats = get_cache_statistics()
print(f"Hit Rate: {stats['statistics']['overall_hit_rate']}%")
```

## Common Patterns

### Pattern 1: Cache beim App-Start

```python
import streamlit as st
from theming.theme_cache import get_theme_cache, load_all_themes

if 'cache_initialized' not in st.session_state:
    cache = get_theme_cache()
    themes = load_all_themes('theming/themes')
    
    for name, data in themes.items():
        cache.cache_theme(name, data)
    
    st.session_state.cache_initialized = True
```

### Pattern 2: CSS mit Caching generieren

```python
def get_or_generate_css(theme_name: str, theme_data: dict) -> str:
    # Prüfe Cache
    cached = get_cached_css(theme_name, theme_data, minified=True)
    if cached:
        return cached
    
    # Generiere
    css_generator = CSSGenerator(theme)
    css = css_generator.generate_full_css()
    
    # Minifiziere
    from theming.performance_optimizer import CSSMinifier
    minified = CSSMinifier.minify(css)
    
    # Cache
    cache_generated_css(theme_name, theme_data, css, minified)
    
    return minified
```

### Pattern 3: Theme-Wechsel mit Cache

```python
def switch_theme(new_theme: str):
    from theming.theme_manager import ThemeManager
    
    manager = ThemeManager()
    
    # Setze Theme
    manager.set_theme(new_theme)
    
    # Cache Theme-Daten
    theme_data = manager.current_theme.to_dict()
    cache_theme_data(new_theme, theme_data)
    
    # Generiere und cache CSS
    css = get_or_generate_css(new_theme, theme_data)
    
    return css
```

### Pattern 4: Cache-Statistiken anzeigen

```python
import streamlit as st

stats = get_cache_statistics()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Theme Hit Rate", 
              f"{stats['statistics']['theme_hit_rate']:.1f}%")

with col2:
    st.metric("CSS Hit Rate", 
              f"{stats['statistics']['css_hit_rate']:.1f}%")

with col3:
    st.metric("Cache Size", 
              f"{stats['session_cache']['cache_size_kb']:.1f} KB")
```

## Streamlit Cache Decorators

### Load Theme from File (1h TTL)

```python
from theming.theme_cache import load_theme_from_file

theme_data = load_theme_from_file('theming/themes/shadcn-default.json')
```

### Load All Themes (30min TTL)

```python
from theming.theme_cache import load_all_themes

themes = load_all_themes('theming/themes')
```

### Generate CSS (Permanent Cache)

```python
from theming.theme_cache import generate_css_cached
import json

css = generate_css_cached(
    theme_name='shadcn-default',
    theme_data_json=json.dumps(theme_data, sort_keys=True),
    css_generator_func=lambda: css_generator.generate_full_css(),
    minified=True
)
```

## Cache Management

### Clear Specific Theme

```python
invalidate_theme_cache('shadcn-dark')
```

### Clear All Themes

```python
invalidate_theme_cache()
```

### Clear Streamlit Caches

```python
from theming.theme_cache import StreamlitCacheIntegration

StreamlitCacheIntegration.clear_theme_cache()
StreamlitCacheIntegration.clear_css_cache()
StreamlitCacheIntegration.clear_all_caches()
```

### Reset Everything

```python
from theming.theme_cache import reset_theme_cache

reset_theme_cache()  # Leert Session + Streamlit Caches
```

## Performance Tips

### ✅ DO

```python
# Cache beim App-Start initialisieren
if 'cache_init' not in st.session_state:
    cache = get_theme_cache()
    # ... initialize
    st.session_state.cache_init = True

# Prüfe Cache vor Generierung
cached = get_cached_css(theme_name, theme_data)
if cached:
    return cached

# Nutze minifiziertes CSS
css = get_cached_css(theme_name, theme_data, minified=True)

# Invalidiere nur bei Änderungen
if theme_changed:
    invalidate_theme_cache(old_theme)
```

### ❌ DON'T

```python
# Nicht: Cache bei jedem Render neu initialisieren
cache = ThemeCache()  # Falsch!

# Nicht: Cache ignorieren
css = css_generator.generate_full_css()  # Langsam!

# Nicht: Unnötig invalidieren
invalidate_theme_cache()  # Bei jedem Render - Falsch!

# Nicht: Unminifiziertes CSS verwenden
css = get_cached_css(theme_name, theme_data, minified=False)  # Groß!
```

## Troubleshooting

### Cache wird nicht genutzt

```python
# Prüfe Cache-Status
cache = get_theme_cache()
info = cache.get_cache_info()
print(f"Cached themes: {info['cached_themes']}")
print(f"Cached CSS: {info['cached_css_count']}")

# Prüfe Statistiken
stats = get_cache_statistics()
print(f"Hit rate: {stats['statistics']['overall_hit_rate']}%")
```

### Cache zu groß

```python
# Prüfe Größe
stats = get_cache_statistics()
size_kb = stats['session_cache']['cache_size_kb']

if size_kb > 1000:  # > 1 MB
    # Invalidiere alte Themes
    invalidate_theme_cache()
```

### Veraltete Daten

```python
# Leere alle Caches
from theming.theme_cache import reset_theme_cache

reset_theme_cache()
```

## API Cheat Sheet

| Function | Purpose | Example |
|----------|---------|---------|
| `get_theme_cache()` | Get cache instance | `cache = get_theme_cache()` |
| `cache_theme_data(name, data)` | Cache theme | `cache_theme_data('dark', data)` |
| `get_cached_theme_data(name)` | Get theme | `data = get_cached_theme_data('dark')` |
| `cache_generated_css(...)` | Cache CSS | `cache_generated_css(name, data, css, min)` |
| `get_cached_css(...)` | Get CSS | `css = get_cached_css(name, data, True)` |
| `invalidate_theme_cache(name)` | Clear cache | `invalidate_theme_cache('dark')` |
| `get_cache_statistics()` | Get stats | `stats = get_cache_statistics()` |
| `reset_theme_cache()` | Reset all | `reset_theme_cache()` |

## Performance Benchmarks

| Operation | Without Cache | With Cache | Speedup |
|-----------|---------------|------------|---------|
| Load theme | ~5ms | ~0.1ms | **50x** |
| Generate CSS | ~80ms | ~0.2ms | **400x** |
| Switch theme | ~100ms | ~5ms | **20x** |

## Integration Examples

### With ThemeManager

```python
from theming.theme_manager import ThemeManager
from theming.theme_cache import get_theme_cache

manager = ThemeManager()
cache = get_theme_cache()

# Set and cache theme
manager.set_theme('shadcn-dark')
cache.cache_theme('shadcn-dark', manager.current_theme.to_dict())

# Generate CSS with caching
css = manager.generate_css(minified=True, use_cache=True)
```

### With PerformanceOptimizer

```python
from theming.performance_optimizer import get_optimizer
from theming.theme_cache import get_theme_cache

optimizer = get_optimizer()
cache = get_theme_cache()

# Use both caching systems
cached = cache.get_cached_css(name, data, minified=True)
if not cached:
    cached = optimizer.generate_optimized_css(name, data, gen_func, True)
    cache.cache_css(name, data, cached, cached)
```

## See Also

- [Full Reference Documentation](../theming/THEME_CACHE_REFERENCE.md)
- [Performance Optimization Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [Theme Manager Guide](THEME_MANAGER_GUIDE.md)
