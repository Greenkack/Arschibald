# Theme Cache System - Usage Examples

## Example 1: Basic Theme Caching

```python
import streamlit as st
from theming.theme_cache import (
    get_theme_cache,
    cache_theme_data,
    get_cached_theme_data
)
from theming.theme_manager import ThemeManager

# Initialisiere Cache beim App-Start
if 'cache_initialized' not in st.session_state:
    cache = get_theme_cache()
    theme_manager = ThemeManager()
    
    # Lade und cache alle verfügbaren Themes
    for theme_name in theme_manager.get_available_themes():
        theme_manager.set_theme(theme_name)
        theme_data = theme_manager.current_theme.to_dict()
        cache_theme_data(theme_name, theme_data)
    
    st.session_state.cache_initialized = True
    st.success(f"✅ {len(theme_manager.get_available_themes())} Themes gecached")

# Theme aus Cache laden (sehr schnell!)
theme_data = get_cached_theme_data('shadcn-default')
if theme_data:
    st.write("Theme aus Cache geladen:", theme_data['display_name'])
```

## Example 2: CSS Generation with Caching

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_cache import (
    get_cached_css,
    cache_generated_css
)
from theming.css_generator import CSSGenerator
from theming.performance_optimizer import CSSMinifier
import time

def generate_css_with_caching(theme_name: str) -> str:
    """Generiert CSS mit Caching für maximale Performance"""
    
    # Theme Manager
    theme_manager = ThemeManager()
    theme_manager.set_theme(theme_name)
    theme_data = theme_manager.current_theme.to_dict()
    
    # Prüfe Cache zuerst
    start_time = time.time()
    cached_css = get_cached_css(theme_name, theme_data, minified=True)
    
    if cached_css:
        cache_time = (time.time() - start_time) * 1000
        st.success(f"✅ CSS aus Cache geladen in {cache_time:.2f}ms")
        return cached_css
    
    # CSS generieren (langsam)
    st.info("⏳ Generiere CSS...")
    start_time = time.time()
    
    css_generator = CSSGenerator(theme_manager.current_theme)
    css = css_generator.generate_full_css()
    
    # Minifizieren
    minified_css = CSSMinifier.minify(css)
    
    generation_time = (time.time() - start_time) * 1000
    
    # In Cache speichern
    cache_generated_css(theme_name, theme_data, css, minified_css)
    
    st.success(f"✅ CSS generiert und gecached in {generation_time:.2f}ms")
    
    return minified_css

# Verwendung
css = generate_css_with_caching('shadcn-dark')
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

## Example 3: Theme Switcher with Caching

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_cache import (
    get_theme_cache,
    cache_theme_data,
    get_cached_css,
    cache_generated_css,
    invalidate_theme_cache
)

def theme_switcher_with_cache():
    """Theme-Selector mit intelligenter Cache-Verwaltung"""
    
    # Theme Manager
    theme_manager = ThemeManager()
    cache = get_theme_cache()
    
    # Aktuelles Theme aus Session State
    if 'current_theme' not in st.session_state:
        st.session_state.current_theme = 'shadcn-default'
    
    # Theme-Selector
    available_themes = theme_manager.get_available_themes()
    theme_display_names = theme_manager.get_theme_display_names()
    
    selected_theme = st.selectbox(
        "Theme auswählen",
        options=available_themes,
        format_func=lambda x: theme_display_names.get(x, x),
        index=available_themes.index(st.session_state.current_theme)
    )
    
    # Theme-Wechsel
    if selected_theme != st.session_state.current_theme:
        st.info(f"🔄 Wechsle zu Theme: {theme_display_names[selected_theme]}")
        
        # Setze neues Theme
        theme_manager.set_theme(selected_theme)
        theme_data = theme_manager.current_theme.to_dict()
        
        # Cache Theme-Daten
        cache_theme_data(selected_theme, theme_data)
        
        # Generiere CSS (mit Caching)
        cached_css = get_cached_css(selected_theme, theme_data, minified=True)
        
        if not cached_css:
            # Generiere und cache
            css = theme_manager.generate_css(minified=True, use_cache=True)
        else:
            css = cached_css
        
        # Injiziere CSS
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        
        # Update Session State
        st.session_state.current_theme = selected_theme
        
        st.success(f"✅ Theme gewechselt zu: {theme_display_names[selected_theme]}")
        st.rerun()

# Verwendung
theme_switcher_with_cache()
```

## Example 4: Cache Statistics Dashboard

```python
import streamlit as st
from theming.theme_cache import get_cache_statistics
import plotly.graph_objects as go

def show_cache_statistics():
    """Zeigt Cache-Statistiken in einem Dashboard"""
    
    st.header("📊 Cache Performance Dashboard")
    
    # Hole Statistiken
    stats = get_cache_statistics()
    
    # Metriken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Theme Hit Rate",
            f"{stats['statistics']['theme_hit_rate']:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "CSS Hit Rate",
            f"{stats['statistics']['css_hit_rate']:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Overall Hit Rate",
            f"{stats['statistics']['overall_hit_rate']:.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            "Cache Size",
            f"{stats['session_cache']['cache_size_kb']:.1f} KB",
            delta=None
        )
    
    # Detaillierte Statistiken
    st.subheader("Detaillierte Statistiken")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Theme Cache:**")
        st.write(f"- Hits: {stats['statistics']['theme_cache_hits']}")
        st.write(f"- Misses: {stats['statistics']['theme_cache_misses']}")
        st.write(f"- Total Loads: {stats['statistics']['total_theme_loads']}")
        st.write(f"- Cached Themes: {stats['session_cache']['cached_themes_count']}")
    
    with col2:
        st.write("**CSS Cache:**")
        st.write(f"- Hits: {stats['statistics']['css_cache_hits']}")
        st.write(f"- Misses: {stats['statistics']['css_cache_misses']}")
        st.write(f"- Total Generations: {stats['statistics']['total_css_generations']}")
        st.write(f"- Cached CSS: {stats['session_cache']['cached_css_count']}")
    
    # Visualisierung
    st.subheader("Cache Hit Rate Visualisierung")
    
    fig = go.Figure(data=[
        go.Bar(
            name='Hits',
            x=['Theme Cache', 'CSS Cache'],
            y=[
                stats['statistics']['theme_cache_hits'],
                stats['statistics']['css_cache_hits']
            ],
            marker_color='green'
        ),
        go.Bar(
            name='Misses',
            x=['Theme Cache', 'CSS Cache'],
            y=[
                stats['statistics']['theme_cache_misses'],
                stats['statistics']['css_cache_misses']
            ],
            marker_color='red'
        )
    ])
    
    fig.update_layout(
        barmode='group',
        title='Cache Hits vs Misses',
        xaxis_title='Cache Type',
        yaxis_title='Count'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gecachte Themes
    st.subheader("Gecachte Themes")
    st.write(stats['session_cache']['cached_themes'])

# Verwendung
show_cache_statistics()
```

## Example 5: Performance Comparison

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_cache import get_cached_css, cache_generated_css
from theming.css_generator import CSSGenerator
from theming.performance_optimizer import CSSMinifier
import time

def performance_comparison():
    """Vergleicht Performance mit und ohne Caching"""
    
    st.header("⚡ Performance Comparison: Cache vs No Cache")
    
    theme_manager = ThemeManager()
    theme_manager.set_theme('shadcn-default')
    theme_data = theme_manager.current_theme.to_dict()
    
    # Test 1: Ohne Cache
    st.subheader("Test 1: CSS Generation ohne Cache")
    
    times_no_cache = []
    for i in range(5):
        start = time.time()
        css_generator = CSSGenerator(theme_manager.current_theme)
        css = css_generator.generate_full_css()
        minified = CSSMinifier.minify(css)
        duration = (time.time() - start) * 1000
        times_no_cache.append(duration)
    
    avg_no_cache = sum(times_no_cache) / len(times_no_cache)
    st.write(f"Durchschnitt: {avg_no_cache:.2f}ms")
    st.write(f"Min: {min(times_no_cache):.2f}ms, Max: {max(times_no_cache):.2f}ms")
    
    # Cache CSS für Test 2
    cache_generated_css('shadcn-default', theme_data, css, minified)
    
    # Test 2: Mit Cache
    st.subheader("Test 2: CSS aus Cache laden")
    
    times_with_cache = []
    for i in range(5):
        start = time.time()
        cached_css = get_cached_css('shadcn-default', theme_data, minified=True)
        duration = (time.time() - start) * 1000
        times_with_cache.append(duration)
    
    avg_with_cache = sum(times_with_cache) / len(times_with_cache)
    st.write(f"Durchschnitt: {avg_with_cache:.2f}ms")
    st.write(f"Min: {min(times_with_cache):.2f}ms, Max: {max(times_with_cache):.2f}ms")
    
    # Vergleich
    st.subheader("📈 Ergebnis")
    
    speedup = avg_no_cache / avg_with_cache
    time_saved = avg_no_cache - avg_with_cache
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Speedup",
            f"{speedup:.1f}x",
            delta=f"{time_saved:.2f}ms gespart"
        )
    
    with col2:
        st.metric(
            "Zeit gespart",
            f"{time_saved:.2f}ms",
            delta=f"{(time_saved/avg_no_cache*100):.1f}% schneller"
        )
    
    # Visualisierung
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[
        go.Bar(
            name='Ohne Cache',
            x=['CSS Generation'],
            y=[avg_no_cache],
            marker_color='red'
        ),
        go.Bar(
            name='Mit Cache',
            x=['CSS Generation'],
            y=[avg_with_cache],
            marker_color='green'
        )
    ])
    
    fig.update_layout(
        title='Performance Vergleich',
        yaxis_title='Zeit (ms)',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Verwendung
performance_comparison()
```

## Example 6: Cache Management UI

```python
import streamlit as st
from theming.theme_cache import (
    get_theme_cache,
    invalidate_theme_cache,
    get_cache_statistics,
    StreamlitCacheIntegration
)

def cache_management_ui():
    """UI für Cache-Verwaltung"""
    
    st.header("🗄️ Cache Management")
    
    cache = get_theme_cache()
    stats = get_cache_statistics()
    
    # Cache-Info
    st.subheader("Cache Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Gecachte Themes:** {stats['session_cache']['cached_themes_count']}")
        st.write(f"**Gecachte CSS:** {stats['session_cache']['cached_css_count']}")
        st.write(f"**Cache-Größe:** {stats['session_cache']['cache_size_kb']:.2f} KB")
    
    with col2:
        st.write(f"**Hit Rate:** {stats['statistics']['overall_hit_rate']:.1f}%")
        st.write(f"**Total Requests:** {stats['statistics']['theme_cache_hits'] + stats['statistics']['theme_cache_misses'] + stats['statistics']['css_cache_hits'] + stats['statistics']['css_cache_misses']}")
    
    # Gecachte Themes anzeigen
    st.subheader("Gecachte Themes")
    
    cached_themes = stats['session_cache']['cached_themes']
    
    if cached_themes:
        for theme_name in cached_themes:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"📦 {theme_name}")
            
            with col2:
                if st.button(f"Invalidieren", key=f"inv_{theme_name}"):
                    invalidate_theme_cache(theme_name)
                    st.success(f"✅ Theme '{theme_name}' invalidiert")
                    st.rerun()
    else:
        st.info("Keine Themes im Cache")
    
    # Cache-Aktionen
    st.subheader("Cache-Aktionen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Session Cache leeren"):
            invalidate_theme_cache()
            st.success("✅ Session Cache geleert")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Streamlit Cache leeren"):
            StreamlitCacheIntegration.clear_all_caches()
            st.success("✅ Streamlit Cache geleert")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Alle Caches leeren"):
            from theming.theme_cache import reset_theme_cache
            reset_theme_cache()
            st.success("✅ Alle Caches geleert")
            st.rerun()

# Verwendung
cache_management_ui()
```

## Example 7: Integration in Main App

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_cache import (
    get_theme_cache,
    load_all_themes,
    cache_theme_data,
    get_cached_css,
    cache_generated_css
)

def initialize_theme_system_with_cache():
    """Initialisiert Theme-System mit Caching beim App-Start"""
    
    # Nur einmal beim App-Start
    if 'theme_system_initialized' not in st.session_state:
        with st.spinner("🎨 Initialisiere Theme-System..."):
            # Theme Manager
            theme_manager = ThemeManager()
            
            # Cache
            cache = get_theme_cache()
            
            # Lade alle Themes mit Streamlit-Caching
            themes = load_all_themes('theming/themes')
            
            # Cache alle Themes
            for theme_name, theme_data in themes.items():
                cache_theme_data(theme_name, theme_data)
            
            # Setze Standard-Theme
            default_theme = 'shadcn-default'
            theme_manager.set_theme(default_theme)
            
            # Generiere und cache CSS
            theme_data = theme_manager.current_theme.to_dict()
            cached_css = get_cached_css(default_theme, theme_data, minified=True)
            
            if not cached_css:
                css = theme_manager.generate_css(minified=True, use_cache=True)
            else:
                css = cached_css
            
            # Injiziere CSS
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            
            # Speichere in Session State
            st.session_state.theme_manager = theme_manager
            st.session_state.current_theme = default_theme
            st.session_state.theme_system_initialized = True
            
            st.success(f"✅ Theme-System initialisiert ({len(themes)} Themes gecached)")

# In gui.py oder main app
def main():
    st.set_page_config(page_title="My App", layout="wide")
    
    # Initialisiere Theme-System mit Caching
    initialize_theme_system_with_cache()
    
    # Rest der App...
    st.title("My Application")
    
    # Theme-Selector in Sidebar
    with st.sidebar:
        from theming.theme_selector_ui import render_theme_selector
        render_theme_selector(st.session_state.theme_manager)

if __name__ == "__main__":
    main()
```

## See Also

- [Theme Cache Reference](THEME_CACHE_REFERENCE.md)
- [Quick Reference Guide](../docs/THEME_CACHE_QUICK_REFERENCE.md)
- [Performance Optimization Guide](../docs/PERFORMANCE_OPTIMIZATION_GUIDE.md)
