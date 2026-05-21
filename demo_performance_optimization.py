"""
Demo: Performance-Optimierung

Demonstriert die Performance-Optimierungen für CSS-Generierung und Component-Rendering.
Zeigt Caching, Minification und Performance-Monitoring.
"""

import streamlit as st
import time
from theming.theme_manager import ThemeManager
from theming.performance_optimizer import (
    get_optimizer,
    reset_optimizer,
    ComponentRenderOptimizer,
    CSSMinifier
)
from components.card import Card
from components.metric_card import MetricCard


def main():
    st.set_page_config(
        page_title="Performance-Optimierung Demo",
        page_
        layout="wide"
    )
    
    st.title(" Performance-Optimierung Demo")
    st.markdown("Demonstriert CSS-Caching, Minification und Performance-Monitoring")
    
    # Initialisiere Theme Manager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    theme_manager = st.session_state.theme_manager
    
    # Tabs für verschiedene Demos
    tab1, tab2, tab3, tab4 = st.tabs([
        " CSS Performance",
        " Caching Demo",
        " Minification",
        "⏱ Component Rendering"
    ])
    
    # Tab 1: CSS Performance
    with tab1:
        st.header("CSS-Generierung Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Ohne Optimierung")
            
            if st.button("CSS generieren (ohne Cache)", key="no_cache"):
                start = time.time()
                css = theme_manager.generate_css(minified=False, use_cache=False)
                duration = (time.time() - start) * 1000
                
                st.success(f" Generiert in {duration:.2f}ms")
                st.metric("CSS-Größe", f"{len(css.encode('utf-8')):,} bytes")
                
                with st.expander("CSS anzeigen (erste 500 Zeichen)"):
                    st.code(css[:500], language="css")
        
        with col2:
            st.subheader("Mit Optimierung")
            
            if st.button("CSS generieren (mit Cache + Minification)", key="with_cache"):
                start = time.time()
                css = theme_manager.generate_css(minified=True, use_cache=True)
                duration = (time.time() - start) * 1000
                
                st.success(f" Generiert in {duration:.2f}ms")
                st.metric("CSS-Größe (minifiziert)", f"{len(css.encode('utf-8')):,} bytes")
                
                with st.expander("Minifiziertes CSS anzeigen (erste 500 Zeichen)"):
                    st.code(css[:500], language="css")
        
        # Performance-Metriken anzeigen
        st.divider()
        st.subheader("Performance-Metriken")
        
        optimizer = get_optimizer()
        metrics = optimizer.get_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Generierungszeit",
                f"{metrics['css_generation_time_ms']:.2f}ms",
                delta="Ziel: < 100ms",
                delta_color="normal" if metrics['css_generation_time_ms'] < 100 else "inverse"
            )
        
        with col2:
            st.metric(
                "Kompression",
                f"{metrics['compression_ratio']:.1f}%"
            )
        
        with col3:
            if 'cache_stats' in metrics:
                st.metric(
                    "Cache Hit-Rate",
                    f"{metrics['cache_stats']['hit_rate']:.1f}%"
                )
        
        with col4:
            st.metric(
                "Requests",
                metrics['total_requests']
            )
        
        # Detaillierte Metriken
        with st.expander(" Detaillierte Metriken"):
            st.json(metrics)
        
        # Performance-Report
        with st.expander(" Performance-Report"):
            report = optimizer.get_performance_report()
            st.text(report)
        
        # Reset-Button
        if st.button(" Metriken zurücksetzen"):
            optimizer.reset_metrics()
            st.rerun()
    
    # Tab 2: Caching Demo
    with tab2:
        st.header("CSS-Caching Demonstration")
        
        st.markdown("""
        Dieser Test zeigt den Unterschied zwischen Cache-Hit und Cache-Miss.
        Beim ersten Aufruf wird CSS generiert (langsam), beim zweiten aus dem Cache geladen (schnell).
        """)
        
        # Theme-Auswahl
        themes = theme_manager.get_available_themes()
        selected_theme = st.selectbox("Theme auswählen", themes)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("1⃣ Erste Generierung (Cache-Miss)", key="cache_miss"):
                # Cache für dieses Theme invalidieren
                optimizer = get_optimizer()
                optimizer.invalidate_cache(selected_theme)
                
                # Theme setzen und CSS generieren
                theme_manager.set_theme(selected_theme)
                
                start = time.time()
                css = theme_manager.generate_css(minified=True, use_cache=True)
                duration = (time.time() - start) * 1000
                
                st.warning(f"⏱ Cache-Miss: {duration:.2f}ms")
                st.info("CSS wurde neu generiert und im Cache gespeichert")
        
        with col2:
            if st.button("2⃣ Zweite Generierung (Cache-Hit)", key="cache_hit"):
                # CSS aus Cache laden
                start = time.time()
                css = theme_manager.generate_css(minified=True, use_cache=True)
                duration = (time.time() - start) * 1000
                
                st.success(f" Cache-Hit: {duration:.2f}ms")
                st.info("CSS wurde aus dem Cache geladen (viel schneller!)")
        
        # Cache-Statistiken
        st.divider()
        st.subheader("Cache-Statistiken")
        
        optimizer = get_optimizer()
        if optimizer.cache:
            cache_stats = optimizer.cache.get_stats()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Cache-Hits", cache_stats['hits'])
            
            with col2:
                st.metric("Cache-Misses", cache_stats['misses'])
            
            with col3:
                st.metric("Hit-Rate", f"{cache_stats['hit_rate']:.1f}%")
            
            # Fortschrittsbalken für Cache-Auslastung
            st.progress(
                cache_stats['cached_items'] / cache_stats['max_size'],
                text=f"Cache-Auslastung: {cache_stats['cached_items']}/{cache_stats['max_size']}"
            )
        
        # Cache leeren
        if st.button(" Cache leeren"):
            optimizer.invalidate_cache()
            st.success("Cache wurde geleert")
            st.rerun()
    
    # Tab 3: Minification
    with tab3:
        st.header("CSS-Minification")
        
        st.markdown("""
        Minification reduziert die CSS-Größe durch Entfernen von Whitespace,
        Kommentaren und unnötigen Zeichen.
        """)
        
        if st.button("CSS minifizieren"):
            # Generiere normales CSS
            css_normal = theme_manager.generate_css(minified=False, use_cache=False)
            
            # Minifiziere CSS
            minifier = CSSMinifier()
            css_minified = minifier.minify(css_normal)
            
            # Berechne Einsparungen
            savings = minifier.calculate_savings(css_normal, css_minified)
            
            # Zeige Ergebnisse
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Original-Größe",
                    f"{savings['original_size_bytes']:,} bytes"
                )
            
            with col2:
                st.metric(
                    "Minifizierte Größe",
                    f"{savings['minified_size_bytes']:,} bytes",
                    delta=f"-{savings['savings_bytes']:,} bytes"
                )
            
            with col3:
                st.metric(
                    "Einsparung",
                    f"{savings['savings_percent']:.1f}%"
                )
            
            # Vergleich anzeigen
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original CSS")
                st.code(css_normal[:500], language="css")
                st.caption(f"Zeilen: {css_normal.count(chr(10))}")
            
            with col2:
                st.subheader("Minifiziertes CSS")
                st.code(css_minified[:500], language="css")
                st.caption(f"Zeilen: {css_minified.count(chr(10))}")
    
    # Tab 4: Component Rendering
    with tab4:
        st.header("Component-Rendering Performance")
        
        st.markdown("""
        Misst die Render-Zeit verschiedener Komponenten.
        Ziel: < 50ms pro Komponente
        """)
        
        # Initialisiere Component-Optimizer
        if 'component_optimizer' not in st.session_state:
            st.session_state.component_optimizer = ComponentRenderOptimizer()
        
        comp_optimizer = st.session_state.component_optimizer
        
        # Anzahl Komponenten
        num_components = st.slider("Anzahl zu rendernder Komponenten", 1, 20, 5)
        
        if st.button(" Komponenten rendern"):
            card = Card(theme_manager)
            metric_card = MetricCard(theme_manager)
            
            # Render Cards
            for i in range(num_components):
                with comp_optimizer.measure_render_time('Card'):
                    card.render(
                        title=f"Test Card {i+1}",
                        content="Dies ist ein Test-Inhalt",
                        variant="default"
                    )
            
            # Render Metric Cards
            for i in range(num_components):
                with comp_optimizer.measure_render_time('MetricCard'):
                    metric_card.render(
                        label=f"Metrik {i+1}",
                        value=f"{1000 + i*100}",
                        trend=5.2 if i % 2 == 0 else -3.1
                    )
            
            st.success(f" {num_components * 2} Komponenten gerendert")
        
        # Render-Statistiken
        st.divider()
        st.subheader("Render-Statistiken")
        
        render_stats = comp_optimizer.get_render_stats()
        
        if render_stats:
            for component, stats in render_stats.items():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(f"{component} - Durchschnitt", f"{stats['avg_ms']:.2f}ms")
                
                with col2:
                    st.metric("Minimum", f"{stats['min_ms']:.2f}ms")
                
                with col3:
                    st.metric("Maximum", f"{stats['max_ms']:.2f}ms")
                
                with col4:
                    st.metric("Anzahl", stats['count'])
                
                # Warnung bei langsamen Komponenten
                if stats['avg_ms'] > 50:
                    st.warning(f" {component} ist langsamer als Ziel (50ms)")
                else:
                    st.success(f" {component} erfüllt Performance-Ziel")
        else:
            st.info("Noch keine Komponenten gerendert")
        
        # Langsame Komponenten
        slow_components = comp_optimizer.get_slow_components(threshold_ms=50.0)
        
        if slow_components:
            st.divider()
            st.subheader(" Langsame Komponenten")
            
            for comp in slow_components:
                st.warning(
                    f"**{comp['component']}**: Durchschnitt {comp['avg_ms']}ms "
                    f"(Max: {comp['max_ms']}ms)"
                )
        
        # Reset-Button
        if st.button(" Statistiken zurücksetzen", key="reset_comp"):
            comp_optimizer.reset_stats()
            st.rerun()
    
    # Sidebar mit Informationen
    with st.sidebar:
        st.header("ℹ Informationen")
        
        st.markdown("""
        ### Performance-Ziele
        
        - **CSS-Generierung**: < 100ms
        - **Component-Rendering**: < 50ms
        - **CSS-Größe**: < 50KB
        - **Cache-Hit-Rate**: > 80%
        
        ### Optimierungen
        
         CSS-Caching (LRU)  
         CSS-Minification  
         Performance-Monitoring  
         Component-Render-Tracking  
        
        ### Features
        
        - Automatisches Caching
        - Intelligente Cache-Invalidierung
        - Kompressionsstatistiken
        - Detaillierte Metriken
        """)
        
        st.divider()
        
        # Globale Aktionen
        st.subheader("Globale Aktionen")
        
        if st.button(" Alles zurücksetzen"):
            reset_optimizer()
            if 'component_optimizer' in st.session_state:
                del st.session_state.component_optimizer
            st.success("Alle Optimierungen zurückgesetzt")
            st.rerun()


if __name__ == "__main__":
    main()
