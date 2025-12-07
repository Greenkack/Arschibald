"""
Demo: Theme Cache System

Demonstriert das Theme-Caching-System mit Performance-Vergleichen
und Cache-Statistiken.
"""

import streamlit as st
import time
from theming.theme_manager import ThemeManager
from theming.theme_cache import (
    get_theme_cache,
    cache_theme_data,
    get_cached_theme_data,
    cache_generated_css,
    get_cached_css,
    invalidate_theme_cache,
    get_cache_statistics,
    load_all_themes,
    StreamlitCacheIntegration,
    reset_theme_cache
)
from theming.css_generator import CSSGenerator
from theming.performance_optimizer import CSSMinifier
import plotly.graph_objects as go


def main():
    st.set_page_config(
        page_title="Theme Cache System Demo",
        page_icon="",
        layout="wide"
    )
    
    st.title(" Theme Cache System Demo")
    st.markdown("---")
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")
        demo_section = st.radio(
            "Wähle Demo:",
            [
                "1. Basic Caching",
                "2. Performance Comparison",
                "3. Cache Statistics",
                "4. Theme Switcher",
                "5. Cache Management"
            ]
        )
    
    # Initialize cache
    if 'cache_initialized' not in st.session_state:
        with st.spinner("Initialisiere Cache..."):
            cache = get_theme_cache()
            theme_manager = ThemeManager()
            
            # Load and cache all themes
            for theme_name in theme_manager.get_available_themes():
                theme_manager.set_theme(theme_name)
                theme_data = theme_manager.current_theme.to_dict()
                cache_theme_data(theme_name, theme_data)
            
            st.session_state.cache_initialized = True
            st.session_state.theme_manager = theme_manager
    
    # Show selected demo
    if demo_section == "1. Basic Caching":
        demo_basic_caching()
    elif demo_section == "2. Performance Comparison":
        demo_performance_comparison()
    elif demo_section == "3. Cache Statistics":
        demo_cache_statistics()
    elif demo_section == "4. Theme Switcher":
        demo_theme_switcher()
    elif demo_section == "5. Cache Management":
        demo_cache_management()


def demo_basic_caching():
    """Demo 1: Basic Theme Caching"""
    st.header("1. Basic Theme Caching")
    
    st.markdown("""
    Diese Demo zeigt die grundlegende Funktionalität des Theme-Caching-Systems.
    """)
    
    cache = get_theme_cache()
    theme_manager = st.session_state.theme_manager
    
    # Theme auswählen
    available_themes = theme_manager.get_available_themes()
    selected_theme = st.selectbox(
        "Theme auswählen:",
        available_themes
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Theme aus Cache laden")
        
        if st.button("Theme aus Cache laden"):
            start = time.time()
            theme_data = get_cached_theme_data(selected_theme)
            duration = (time.time() - start) * 1000
            
            if theme_data:
                st.success(f" Theme geladen in {duration:.3f}ms")
                st.json({
                    "name": theme_data['name'],
                    "display_name": theme_data['display_name'],
                    "colors_count": len(theme_data['colors']),
                    "cached": True
                })
            else:
                st.error(" Theme nicht im Cache")
    
    with col2:
        st.subheader("Theme neu laden")
        
        if st.button("Theme neu laden (ohne Cache)"):
            start = time.time()
            theme_manager.set_theme(selected_theme)
            theme_data = theme_manager.current_theme.to_dict()
            duration = (time.time() - start) * 1000
            
            st.info(f"⏱ Theme geladen in {duration:.3f}ms")
            st.json({
                "name": theme_data['name'],
                "display_name": theme_data['display_name'],
                "colors_count": len(theme_data['colors']),
                "cached": False
            })
            
            # Cache it
            cache_theme_data(selected_theme, theme_data)
            st.success(" Theme wurde gecached")


def demo_performance_comparison():
    """Demo 2: Performance Comparison"""
    st.header("2. Performance Comparison")
    
    st.markdown("""
    Vergleicht die Performance von CSS-Generierung mit und ohne Caching.
    """)
    
    theme_manager = st.session_state.theme_manager
    theme_manager.set_theme('shadcn-default')
    theme_data = theme_manager.current_theme.to_dict()
    
    num_iterations = st.slider("Anzahl Iterationen:", 1, 10, 5)
    
    if st.button(" Performance-Test starten"):
        # Test 1: Ohne Cache
        st.subheader("Test 1: CSS Generation ohne Cache")
        
        progress_bar = st.progress(0)
        times_no_cache = []
        
        for i in range(num_iterations):
            start = time.time()
            css_generator = CSSGenerator(theme_manager.current_theme)
            css = css_generator.generate_full_css()
            minified = CSSMinifier.minify(css)
            duration = (time.time() - start) * 1000
            times_no_cache.append(duration)
            progress_bar.progress((i + 1) / num_iterations)
        
        avg_no_cache = sum(times_no_cache) / len(times_no_cache)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Durchschnitt", f"{avg_no_cache:.2f}ms")
        with col2:
            st.metric("Min", f"{min(times_no_cache):.2f}ms")
        with col3:
            st.metric("Max", f"{max(times_no_cache):.2f}ms")
        
        # Cache CSS für Test 2
        cache_generated_css('shadcn-default', theme_data, css, minified)
        
        # Test 2: Mit Cache
        st.subheader("Test 2: CSS aus Cache laden")
        
        progress_bar = st.progress(0)
        times_with_cache = []
        
        for i in range(num_iterations):
            start = time.time()
            cached_css = get_cached_css('shadcn-default', theme_data, minified=True)
            duration = (time.time() - start) * 1000
            times_with_cache.append(duration)
            progress_bar.progress((i + 1) / num_iterations)
        
        avg_with_cache = sum(times_with_cache) / len(times_with_cache)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Durchschnitt", f"{avg_with_cache:.2f}ms")
        with col2:
            st.metric("Min", f"{min(times_with_cache):.2f}ms")
        with col3:
            st.metric("Max", f"{max(times_with_cache):.2f}ms")
        
        # Vergleich
        st.subheader(" Ergebnis")
        
        speedup = avg_no_cache / avg_with_cache if avg_with_cache > 0 else 0
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
        fig = go.Figure(data=[
            go.Bar(
                name='Ohne Cache',
                x=['CSS Generation'],
                y=[avg_no_cache],
                marker_color='#ef4444',
                text=[f"{avg_no_cache:.2f}ms"],
                textposition='auto'
            ),
            go.Bar(
                name='Mit Cache',
                x=['CSS Generation'],
                y=[avg_with_cache],
                marker_color='#22c55e',
                text=[f"{avg_with_cache:.2f}ms"],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Performance Vergleich',
            yaxis_title='Zeit (ms)',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def demo_cache_statistics():
    """Demo 3: Cache Statistics"""
    st.header("3. Cache Statistics Dashboard")
    
    st.markdown("""
    Zeigt detaillierte Statistiken über die Cache-Performance.
    """)
    
    stats = get_cache_statistics()
    
    # Metriken
    st.subheader(" Haupt-Metriken")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
            "Overall Hit Rate",
            f"{stats['statistics']['overall_hit_rate']:.1f}%"
        )
    
    with col4:
        st.metric(
            "Cache Size",
            f"{stats['session_cache']['cache_size_kb']:.1f} KB"
        )
    
    # Detaillierte Statistiken
    st.subheader(" Detaillierte Statistiken")
    
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
    st.subheader(" Cache Hit Rate Visualisierung")
    
    fig = go.Figure(data=[
        go.Bar(
            name='Hits',
            x=['Theme Cache', 'CSS Cache'],
            y=[
                stats['statistics']['theme_cache_hits'],
                stats['statistics']['css_cache_hits']
            ],
            marker_color='#22c55e'
        ),
        go.Bar(
            name='Misses',
            x=['Theme Cache', 'CSS Cache'],
            y=[
                stats['statistics']['theme_cache_misses'],
                stats['statistics']['css_cache_misses']
            ],
            marker_color='#ef4444'
        )
    ])
    
    fig.update_layout(
        barmode='group',
        title='Cache Hits vs Misses',
        xaxis_title='Cache Type',
        yaxis_title='Count',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gecachte Themes
    st.subheader(" Gecachte Themes")
    
    cached_themes = stats['session_cache']['cached_themes']
    if cached_themes:
        st.write(", ".join(cached_themes))
    else:
        st.info("Keine Themes im Cache")


def demo_theme_switcher():
    """Demo 4: Theme Switcher with Caching"""
    st.header("4. Theme Switcher mit Caching")
    
    st.markdown("""
    Demonstriert Theme-Wechsel mit intelligenter Cache-Verwaltung.
    """)
    
    theme_manager = st.session_state.theme_manager
    
    # Aktuelles Theme
    if 'demo_current_theme' not in st.session_state:
        st.session_state.demo_current_theme = 'shadcn-default'
    
    # Theme-Selector
    available_themes = theme_manager.get_available_themes()
    theme_display_names = theme_manager.get_theme_display_names()
    
    selected_theme = st.selectbox(
        "Theme auswählen:",
        options=available_themes,
        format_func=lambda x: theme_display_names.get(x, x),
        index=available_themes.index(st.session_state.demo_current_theme)
    )
    
    # Theme-Wechsel
    if selected_theme != st.session_state.demo_current_theme:
        with st.spinner(f"Wechsle zu {theme_display_names[selected_theme]}..."):
            start = time.time()
            
            # Setze Theme
            theme_manager.set_theme(selected_theme)
            theme_data = theme_manager.current_theme.to_dict()
            
            # Cache Theme
            cache_theme_data(selected_theme, theme_data)
            
            # Hole oder generiere CSS
            cached_css = get_cached_css(selected_theme, theme_data, minified=True)
            
            if cached_css:
                css = cached_css
                cache_status = "aus Cache geladen"
            else:
                css = theme_manager.generate_css(minified=True, use_cache=True)
                cache_status = "neu generiert und gecached"
            
            duration = (time.time() - start) * 1000
            
            # Update Session State
            st.session_state.demo_current_theme = selected_theme
            
            st.success(f" Theme gewechselt in {duration:.2f}ms ({cache_status})")
    
    # Zeige aktuelles Theme
    st.subheader("Aktuelles Theme")
    
    current_theme = theme_manager.current_theme
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {current_theme.name}")
        st.write(f"**Display Name:** {current_theme.display_name}")
    
    with col2:
        # Zeige Farben
        st.write("**Primärfarben:**")
        st.color_picker("Primary", current_theme.colors.primary, disabled=True)
        st.color_picker("Secondary", current_theme.colors.secondary, disabled=True)


def demo_cache_management():
    """Demo 5: Cache Management"""
    st.header("5. Cache Management")
    
    st.markdown("""
    Verwalte den Cache: Invalidiere Themes, leere Caches, zeige Informationen.
    """)
    
    cache = get_theme_cache()
    stats = get_cache_statistics()
    
    # Cache-Info
    st.subheader(" Cache Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Gecachte Themes:** {stats['session_cache']['cached_themes_count']}")
        st.write(f"**Gecachte CSS:** {stats['session_cache']['cached_css_count']}")
        st.write(f"**Cache-Größe:** {stats['session_cache']['cache_size_kb']:.2f} KB")
    
    with col2:
        st.write(f"**Hit Rate:** {stats['statistics']['overall_hit_rate']:.1f}%")
        total_requests = (stats['statistics']['theme_cache_hits'] + 
                         stats['statistics']['theme_cache_misses'] + 
                         stats['statistics']['css_cache_hits'] + 
                         stats['statistics']['css_cache_misses'])
        st.write(f"**Total Requests:** {total_requests}")
    
    # Gecachte Themes
    st.subheader(" Gecachte Themes")
    
    cached_themes = stats['session_cache']['cached_themes']
    
    if cached_themes:
        for theme_name in cached_themes:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f" {theme_name}")
            
            with col2:
                if st.button("Invalidieren", key=f"inv_{theme_name}"):
                    invalidate_theme_cache(theme_name)
                    st.success(f" Theme '{theme_name}' invalidiert")
                    st.rerun()
    else:
        st.info("Keine Themes im Cache")
    
    # Cache-Aktionen
    st.subheader(" Cache-Aktionen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Session Cache leeren"):
            invalidate_theme_cache()
            st.success(" Session Cache geleert")
            st.rerun()
    
    with col2:
        if st.button("Streamlit Cache leeren"):
            StreamlitCacheIntegration.clear_all_caches()
            st.success(" Streamlit Cache geleert")
            st.rerun()
    
    with col3:
        if st.button("Alle Caches leeren"):
            reset_theme_cache()
            st.success(" Alle Caches geleert")
            st.rerun()


if __name__ == "__main__":
    main()
