# Theme Cache System - Reference Documentation

## Overview

Das Theme Cache System bietet ein umfassendes Caching-System für Theme-Daten und generiertes CSS. Es kombiniert Session State Caching mit Streamlit's `@st.cache_data` Decorator für optimale Performance.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Theme Cache System                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Session State   │      │  Streamlit       │        │
│  │  Cache           │      │  @cache_data     │        │
│  │                  │      │                  │        │
│  │  - Themes        │      │  - File Loading  │        │
│  │  - CSS           │      │  - CSS Gen       │        │
│  │  - Statistics    │      │  - TTL Support   │        │
│  └──────────────────┘      └──────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  Performance Optimizer Integration       │          │
│  │  - CSS Minification                      │          │
│  │  - LRU Cache                             │          │
│  │  - Performance Metrics                   │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

## Core Classes

### ThemeCache

Hauptklasse für Theme- und CSS-Caching.

```python
from theming.theme_cache import ThemeCache

cache = ThemeCache()

# Theme cachen
cache.cache_theme('shadcn-default', theme_data)

# Theme aus Cache holen
theme_data = cache.get_cached_theme('shadcn-default')

# CSS cachen
cache.cache_css('shadcn-default', theme_data, css, minified_css)

# CSS aus Cache holen
css = cache.get_cached_css('shadcn-default', theme_data, minified=True)

# Cache invalidieren
cache.invalidate_theme('shadcn-default')  # Spezifisches Theme
cache.invalidate_all()  # Alle Themes
```

### CacheStatistics

Statistiken für Cache-Performance.

```python
stats = cache.get_statistics()

print(f"Theme Hit Rate: {stats.theme_hit_rate:.2f}%")
print(f"CSS Hit Rate: {stats.css_hit_rate:.2f}%")
print(f"Overall Hit Rate: {stats.overall_hit_rate:.2f}%")
print(f"Cache Size: {stats.cache_size_bytes / 1024:.2f} KB")

# Als Dictionary
stats_dict = stats.to_dict()
```

### StreamlitCacheIntegration

Integration mit Streamlit's Caching-System.

```python
from theming.theme_cache import StreamlitCacheIntegration

# Cache leeren
StreamlitCacheIntegration.clear_theme_cache()
StreamlitCacheIntegration.clear_css_cache()
StreamlitCacheIntegration.clear_all_caches()

# Cache-Stats
stats = StreamlitCacheIntegration.get_cache_stats()
```

## Convenience Functions

### Theme Caching

```python
from theming.theme_cache import (
    cache_theme_data,
    get_cached_theme_data,
    invalidate_theme_cache
)

# Theme cachen
cache_theme_data('shadcn-dark', theme_data)

# Theme abrufen
theme_data = get_cached_theme_data('shadcn-dark')

# Cache invalidieren
invalidate_theme_cache('shadcn-dark')  # Spezifisch
invalidate_theme_cache()  # Alle
```

### CSS Caching

```python
from theming.theme_cache import (
    cache_generated_css,
    get_cached_css
)

# CSS cachen
cache_generated_css('shadcn-dark', theme_data, css, minified_css)

# CSS abrufen
css = get_cached_css('shadcn-dark', theme_data, minified=True)
```

### Statistics

```python
from theming.theme_cache import get_cache_statistics

stats = get_cache_statistics()

print("Session Cache:")
print(f"  Cached Themes: {stats['session_cache']['cached_themes_count']}")
print(f"  Cached CSS: {stats['session_cache']['cached_css_count']}")
print(f"  Cache Size: {stats['session_cache']['cache_size_kb']} KB")

print("\nStatistics:")
print(f"  Theme Hit Rate: {stats['statistics']['theme_hit_rate']}%")
print(f"  CSS Hit Rate: {stats['statistics']['css_hit_rate']}%")
print(f"  Overall Hit Rate: {stats['statistics']['overall_hit_rate']}%")
```

## Streamlit Cache Decorators

### load_theme_from_file

Lädt Theme aus Datei mit 1-Stunden-Cache.

```python
from theming.theme_cache import load_theme_from_file

theme_data = load_theme_from_file('theming/themes/shadcn-default.json')
```

### load_all_themes

Lädt alle Themes aus Verzeichnis mit 30-Minuten-Cache.

```python
from theming.theme_cache import load_all_themes

themes = load_all_themes('theming/themes')
# Returns: {'shadcn-default': {...}, 'shadcn-dark': {...}, ...}
```

### generate_css_cached

Generiert CSS mit permanentem Cache.

```python
from theming.theme_cache import generate_css_cached
import json

def css_gen_func():
    # CSS-Generierung
    return css_generator.generate_full_css()

css = generate_css_cached(
    theme_name='shadcn-default',
    theme_data_json=json.dumps(theme_data, sort_keys=True),
    css_generator_func=css_gen_func,
    minified=True
)
```

## Integration mit ThemeManager

```python
from theming.theme_manager import ThemeManager
from theming.theme_cache import get_theme_cache

# ThemeManager initialisieren
theme_manager = ThemeManager()

# Cache-Instanz holen
cache = get_theme_cache()

# Theme setzen und cachen
theme_manager.set_theme('shadcn-dark')
theme_data = theme_manager.current_theme.to_dict()
cache.cache_theme('shadcn-dark', theme_data)

# CSS generieren mit Caching
css = theme_manager.generate_css(minified=True, use_cache=True)
```

## Integration mit PerformanceOptimizer

```python
from theming.performance_optimizer import get_optimizer
from theming.theme_cache import get_theme_cache

# Beide Systeme nutzen
optimizer = get_optimizer()
cache = get_theme_cache()

# CSS generieren mit beiden Caching-Systemen
def generate_css():
    # Prüfe Theme-Cache zuerst
    cached_css = cache.get_cached_css(theme_name, theme_data, minified=True)
    if cached_css:
        return cached_css
    
    # Nutze Performance-Optimizer
    css = optimizer.generate_optimized_css(
        theme_name,
        theme_data,
        css_generator_func,
        minified=True
    )
    
    # Cache in Theme-Cache
    cache.cache_css(theme_name, theme_data, css, css)
    
    return css
```

## Cache Invalidation Strategies

### Bei Theme-Wechsel

```python
def switch_theme(new_theme_name: str):
    # Invalidiere altes Theme
    if current_theme:
        invalidate_theme_cache(current_theme)
    
    # Setze neues Theme
    theme_manager.set_theme(new_theme_name)
    
    # Cache neues Theme
    theme_data = theme_manager.current_theme.to_dict()
    cache_theme_data(new_theme_name, theme_data)
```

### Bei Theme-Datei-Änderung

```python
def reload_theme(theme_name: str):
    # Invalidiere Cache
    invalidate_theme_cache(theme_name)
    
    # Lade Theme neu
    theme_manager.reload_theme(theme_name)
    
    # Cache neu
    theme_data = theme_manager.current_theme.to_dict()
    cache_theme_data(theme_name, theme_data)
```

### Periodische Invalidierung

```python
import time

def periodic_cache_cleanup(interval_seconds: int = 3600):
    """Leert Cache alle X Sekunden"""
    last_cleanup = time.time()
    
    if time.time() - last_cleanup > interval_seconds:
        invalidate_theme_cache()
        last_cleanup = time.time()
```

## Performance Monitoring

### Cache-Statistiken anzeigen

```python
import streamlit as st
from theming.theme_cache import get_cache_statistics

stats = get_cache_statistics()

st.subheader("Cache Performance")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Theme Hit Rate",
        f"{stats['statistics']['theme_hit_rate']:.1f}%"
    )

with col2:
    st.metric(
        "CSS Hit Rate",
        f"{stats['statistics']['css_hit_rate']:.1f}%"
    )

with col3:
    st.metric(
        "Cache Size",
        f"{stats['session_cache']['cache_size_kb']:.1f} KB"
    )
```

### Performance-Vergleich

```python
import time

# Ohne Cache
start = time.time()
css = css_generator.generate_full_css()
time_no_cache = (time.time() - start) * 1000

# Mit Cache
start = time.time()
css = get_cached_css(theme_name, theme_data, minified=True)
time_with_cache = (time.time() - start) * 1000

speedup = time_no_cache / time_with_cache
print(f"Speedup: {speedup:.1f}x faster with cache")
```

## Best Practices

### 1. Cache beim App-Start initialisieren

```python
if 'theme_cache_initialized' not in st.session_state:
    cache = get_theme_cache()
    
    # Lade alle Themes in Cache
    themes = load_all_themes('theming/themes')
    for name, data in themes.items():
        cache.cache_theme(name, data)
    
    st.session_state.theme_cache_initialized = True
```

### 2. CSS nur einmal generieren

```python
def get_or_generate_css(theme_name: str, theme_data: Dict) -> str:
    # Prüfe Cache zuerst
    cached_css = get_cached_css(theme_name, theme_data, minified=True)
    if cached_css:
        return cached_css
    
    # Generiere CSS
    css_generator = CSSGenerator(theme)
    css = css_generator.generate_full_css()
    
    # Minifiziere
    from theming.performance_optimizer import CSSMinifier
    minified_css = CSSMinifier.minify(css)
    
    # Cache
    cache_generated_css(theme_name, theme_data, css, minified_css)
    
    return minified_css
```

### 3. Cache-Statistiken loggen

```python
from theming.theme_logger import get_logger

logger = get_logger()

stats = get_cache_statistics()
logger.info(f"Cache Stats: {stats['statistics']}")
```

### 4. Cache bei Fehler invalidieren

```python
try:
    css = get_cached_css(theme_name, theme_data)
except Exception as e:
    logger.error(f"Cache error: {e}")
    invalidate_theme_cache(theme_name)
    # Regeneriere
    css = generate_css_fresh(theme_name, theme_data)
```

## Troubleshooting

### Problem: Cache wird nicht genutzt

**Lösung:**
```python
# Prüfe ob Cache initialisiert ist
cache = get_theme_cache()
info = cache.get_cache_info()
print(f"Cached themes: {info['cached_themes']}")

# Prüfe Statistiken
stats = cache.get_statistics()
print(f"Hit rate: {stats.overall_hit_rate}%")
```

### Problem: Cache zu groß

**Lösung:**
```python
# Invalidiere alte Themes
cache = get_theme_cache()
info = cache.get_cache_info()

if info['cache_size_kb'] > 1000:  # > 1 MB
    # Invalidiere alle außer aktuellem Theme
    current = theme_manager.get_current_theme()
    for theme_name in info['cached_themes']:
        if theme_name != current:
            cache.invalidate_theme(theme_name)
```

### Problem: Veraltete Daten im Cache

**Lösung:**
```python
# Leere Streamlit-Caches
from theming.theme_cache import StreamlitCacheIntegration

StreamlitCacheIntegration.clear_all_caches()

# Leere Session-Cache
invalidate_theme_cache()
```

## API Reference

### ThemeCache Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `cache_theme(name, data)` | Cached Theme-Daten | None |
| `get_cached_theme(name)` | Holt gecachtes Theme | Dict or None |
| `cache_css(name, data, css, min_css)` | Cached CSS | None |
| `get_cached_css(name, data, minified)` | Holt gecachtes CSS | str or None |
| `invalidate_theme(name)` | Invalidiert Theme | None |
| `invalidate_all()` | Invalidiert alles | None |
| `get_statistics()` | Holt Statistiken | CacheStatistics |
| `get_cache_info()` | Holt Cache-Info | Dict |

### Convenience Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `cache_theme_data(name, data)` | Cached Theme | None |
| `get_cached_theme_data(name)` | Holt Theme | Dict or None |
| `cache_generated_css(...)` | Cached CSS | None |
| `get_cached_css(...)` | Holt CSS | str or None |
| `invalidate_theme_cache(name)` | Invalidiert | None |
| `get_cache_statistics()` | Holt Stats | Dict |
| `get_theme_cache()` | Holt Cache-Instanz | ThemeCache |
| `reset_theme_cache()` | Reset Cache | None |

### Streamlit Decorators

| Decorator | TTL | Description |
|-----------|-----|-------------|
| `@load_theme_from_file` | 1h | Lädt Theme aus Datei |
| `@load_all_themes` | 30min | Lädt alle Themes |
| `@generate_css_cached` | ∞ | Generiert CSS |

## Performance Benchmarks

Typische Performance-Verbesserungen mit Caching:

| Operation | Ohne Cache | Mit Cache | Speedup |
|-----------|------------|-----------|---------|
| Theme laden | ~5ms | ~0.1ms | 50x |
| CSS generieren | ~80ms | ~0.2ms | 400x |
| Theme wechseln | ~100ms | ~5ms | 20x |

## See Also

- [Performance Optimizer Reference](PERFORMANCE_OPTIMIZER_REFERENCE.md)
- [Theme Manager Reference](THEME_MANAGER_REFERENCE.md)
- [Error Handling Reference](ERROR_HANDLING_REFERENCE.md)
- [Logging System Reference](LOGGING_SYSTEM_REFERENCE.md)
