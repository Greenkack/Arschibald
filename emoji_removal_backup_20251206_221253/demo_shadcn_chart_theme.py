"""
Demo: shadcn/ui Chart Theme

Demonstriert alle Features des Chart-Styling-Systems.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from theming.theme_manager import ThemeManager
from utils.shadcn_chart_theme import (
    apply_chart_theme,
    create_line_chart,
    create_area_chart,
    create_bar_chart,
    create_pie_chart,
    create_themed_figure,
    get_chart_colors,
    apply_responsive_layout,
    set_chart_title,
    add_chart_annotations
)


def main():
    st.set_page_config(page_title="shadcn/ui Chart Theme Demo", layout="wide")
    
    st.title("📊 shadcn/ui Chart Theme Demo")
    st.markdown("Demonstriert das Chart-Styling-System mit verschiedenen Chart-Typen")
    
    # Initialisiere Theme Manager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()
        st.session_state.theme_manager.set_theme('shadcn-default')
    
    theme_manager = st.session_state.theme_manager
    
    # Sidebar: Theme-Auswahl
    with st.sidebar:
        st.header("⚙️ Einstellungen")
        
        # Theme Selector
        available_themes = theme_manager.get_available_themes()
        theme_names = theme_manager.get_theme_display_names()
        
        current_theme = st.selectbox(
            "Theme",
            options=available_themes,
            format_func=lambda x: theme_names.get(x, x),
            index=available_themes.index(theme_manager.current_theme.name) if theme_manager.current_theme else 0
        )
        
        if current_theme != theme_manager.current_theme.name:
            theme_manager.set_theme(current_theme)
            st.rerun()
        
        st.divider()
        
        # Chart-Optionen
        st.subheader("Chart-Optionen")
        enable_spline = st.checkbox("Glatte Spline-Kurven", value=True)
        enable_gradients = st.checkbox("Gradient-Fills", value=True)
        mobile_layout = st.checkbox("Mobile Layout", value=False)
        
        st.divider()
        
        # Theme-Farben anzeigen
        st.subheader("Theme-Farben")
        colors = get_chart_colors(theme_manager)
        for i, color in enumerate(colors, 1):
            st.markdown(
                f'<div style="background: {color}; padding: 10px; border-radius: 4px; '
                f'color: white; text-align: center; margin-bottom: 5px;">'
                f'Chart {i}: {color}</div>',
                unsafe_allow_html=True
            )
    
    # Hauptbereich: Chart-Demos
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Linien-Charts",
        "📊 Area-Charts",
        "📊 Bar-Charts",
        "🥧 Pie-Charts",
        "🔥 Heatmaps",
        "🎨 Erweitert"
    ])
    
    # Tab 1: Linien-Charts
    with tab1:
        st.header("Linien-Charts mit Spline-Kurven")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Einfacher Linien-Chart")
            
            # Daten generieren
            x = list(range(1, 13))
            y = [20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55, 60]
            
            # Chart erstellen
            fig = create_line_chart(
                x=x,
                y=y,
                name="Umsatz",
                theme_manager=theme_manager
            )
            
            fig = set_chart_title(
                fig,
                "Monatlicher Umsatz",
                "Januar - Dezember 2024",
                theme_manager
            )
            
            if mobile_layout:
                fig = apply_responsive_layout(fig, mobile=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Multi-Linien-Chart")
            
            # Mehrere Linien
            fig = go.Figure()
            
            x = list(range(1, 13))
            y1 = [20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55, 60]
            y2 = [15, 20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55]
            y3 = [10, 15, 20, 25, 30, 28, 35, 40, 38, 45, 50, 48]
            
            fig.add_trace(go.Scatter(x=x, y=y1, name="Produkt A", mode='lines+markers'))
            fig.add_trace(go.Scatter(x=x, y=y2, name="Produkt B", mode='lines+markers'))
            fig.add_trace(go.Scatter(x=x, y=y3, name="Produkt C", mode='lines+markers'))
            
            fig = apply_chart_theme(fig, theme_manager, enable_spline=enable_spline)
            fig = set_chart_title(fig, "Produktvergleich", theme_manager=theme_manager)
            
            if mobile_layout:
                fig = apply_responsive_layout(fig, mobile=True)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Area-Charts
    with tab2:
        st.header("Area-Charts mit Gradient-Fills")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Einfacher Area-Chart")
            
            x = list(range(1, 13))
            y = [20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55, 60]
            
            fig = create_area_chart(
                x=x,
                y=y,
                name="Energieproduktion",
                theme_manager=theme_manager
            )
            
            fig = set_chart_title(
                fig,
                "Solare Energieproduktion",
                "kWh pro Monat",
                theme_manager
            )
            
            if mobile_layout:
                fig = apply_responsive_layout(fig, mobile=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Gestapelter Area-Chart")
            
            fig = go.Figure()
            
            x = list(range(1, 13))
            y1 = [20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55, 60]
            y2 = [15, 20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55]
            
            fig.add_trace(go.Scatter(
                x=x, y=y1,
                name="PV-Anlage 1",
                mode='lines',
                fill='tozeroy',
                stackgroup='one'
            ))
            
            fig.add_trace(go.Scatter(
                x=x, y=y2,
                name="PV-Anlage 2",
                mode='lines',
                fill='tonexty',
                stackgroup='one'
            ))
            
            fig = apply_chart_theme(fig, theme_manager, enable_gradients=enable_gradients)
            fig = set_chart_title(fig, "Gesamtproduktion", theme_manager=theme_manager)
            
            if mobile_layout:
                fig = apply_responsive_layout(fig, mobile=True)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Bar-Charts
    with tab3:
        st.header("Bar-Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vertikaler Bar-Chart")
            
            categories = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun']
            values = [30, 45, 35, 50, 40, 55]
            
            fig = create_bar_chart(
                x=categories,
                y=values,
                name="Verkäufe",
                theme_manager=theme_manager
            )
            
            fig = set_chart_title(fig, "Monatliche Verkäufe", theme_manager=theme_manager)
            
            if mobile_layout:
                fig = apply_responsive_layout(fig, mobile=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Gruppierter Bar-Chart")
            
            categories = ['Q1', 'Q2', 'Q3', 'Q4']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=categories, y=[20, 30, 25, 35], name='2023'))
            fig.add_trace(go.Bar(x=categories, y=[25, 35, 30, 40], name='2024'))
            
            fig = apply_chart_theme(fig, theme_manager)
            fig = set_chart_title(fig, "Quartalsvergleich", theme_manager=theme_manager)
            
            if mobile_layout:
                fig = apply_responsive_layout(fig, mobile=True)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Pie-Charts
    with tab4:
        st.header("Pie-Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Einfacher Pie-Chart")
            
            labels = ['Solar', 'Wind', 'Wasser', 'Biomasse', 'Andere']
            values = [35, 25, 20, 15, 5]
            
            fig = create_pie_chart(
                labels=labels,
                values=values,
                theme_manager=theme_manager,
                hole=0.3
            )
            
            fig = set_chart_title(fig, "Energiequellen", theme_manager=theme_manager)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Donut-Chart")
            
            labels = ['Privatkunden', 'Gewerbe', 'Industrie', 'Öffentlich']
            values = [40, 30, 20, 10]
            
            fig = create_pie_chart(
                labels=labels,
                values=values,
                theme_manager=theme_manager,
                hole=0.5
            )
            
            fig = set_chart_title(fig, "Kundenverteilung", theme_manager=theme_manager)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 5: Heatmaps
    with tab5:
        st.header("Heatmaps")
        
        st.subheader("Korrelations-Heatmap")
        
        # Generiere Korrelationsmatrix
        np.random.seed(42)
        data = np.random.rand(5, 5)
        data = (data + data.T) / 2  # Symmetrisch machen
        np.fill_diagonal(data, 1)  # Diagonale = 1
        
        labels = ['Temperatur', 'Einstrahlung', 'Leistung', 'Effizienz', 'Ertrag']
        
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=labels,
            y=labels,
            colorscale='RdYlGn',
            text=np.round(data, 2),
            texttemplate='%{text}',
            textfont={"size": 12}
        ))
        
        fig = apply_chart_theme(fig, theme_manager)
        fig = set_chart_title(fig, "Korrelationsmatrix", theme_manager=theme_manager)
        
        if mobile_layout:
            fig = apply_responsive_layout(fig, mobile=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 6: Erweiterte Features
    with tab6:
        st.header("Erweiterte Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Chart mit Annotationen")
            
            x = list(range(1, 13))
            y = [20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55, 60]
            
            fig = create_line_chart(x=x, y=y, name="Wert", theme_manager=theme_manager)
            
            # Annotationen hinzufügen
            annotations = [
                dict(
                    x=6,
                    y=40,
                    text="Peak",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40
                ),
                dict(
                    x=12,
                    y=60,
                    text="Ziel erreicht!",
                    showarrow=True,
                    arrowhead=2,
                    ax=-40,
                    ay=-40
                )
            ]
            
            fig = add_chart_annotations(fig, annotations, theme_manager)
            fig = set_chart_title(fig, "Chart mit Annotationen", theme_manager=theme_manager)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Kombinierter Chart")
            
            x = list(range(1, 13))
            y_bar = [20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55, 60]
            y_line = [15, 20, 25, 30, 28, 35, 40, 38, 45, 50, 48, 55]
            
            fig = go.Figure()
            
            # Bar-Trace
            fig.add_trace(go.Bar(
                x=x,
                y=y_bar,
                name="Ist-Wert"
            ))
            
            # Line-Trace
            fig.add_trace(go.Scatter(
                x=x,
                y=y_line,
                name="Soll-Wert",
                mode='lines+markers',
                yaxis='y2'
            ))
            
            # Zweite Y-Achse
            fig.update_layout(
                yaxis2=dict(
                    overlaying='y',
                    side='right'
                )
            )
            
            fig = apply_chart_theme(fig, theme_manager, enable_spline=enable_spline)
            fig = set_chart_title(fig, "Ist-Soll-Vergleich", theme_manager=theme_manager)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.divider()
    st.markdown("""
    ### 📚 Features
    
    - ✅ **Automatisches Theme-Styling**: Alle Charts passen sich dem gewählten Theme an
    - ✅ **Glatte Spline-Kurven**: Moderne, fließende Linien statt eckiger Verbindungen
    - ✅ **Gradient-Fills**: Schöne Farbverläufe für Area-Charts
    - ✅ **Responsive Layouts**: Optimiert für Desktop und Mobile
    - ✅ **Dark Mode Support**: Automatische Anpassung an helle/dunkle Themes
    - ✅ **Konsistente Farben**: 5 harmonische Chart-Farben pro Theme
    - ✅ **Moderne Schriftarten**: Inter/System-Fonts für professionelles Aussehen
    - ✅ **Hover-Effekte**: Gestylte Tooltips im Theme-Design
    
    ### 💡 Verwendung
    
    ```python
    from theming.theme_manager import ThemeManager
    from utils.shadcn_chart_theme import apply_chart_theme
    import plotly.graph_objects as go
    
    # Theme Manager initialisieren
    theme_manager = ThemeManager()
    theme_manager.set_theme('shadcn-default')
    
    # Chart erstellen
    fig = go.Figure(data=[go.Scatter(x=[1,2,3], y=[4,5,6])])
    
    # Theme anwenden
    fig = apply_chart_theme(fig, theme_manager)
    
    # Anzeigen
    st.plotly_chart(fig)
    ```
    """)


if __name__ == "__main__":
    main()
