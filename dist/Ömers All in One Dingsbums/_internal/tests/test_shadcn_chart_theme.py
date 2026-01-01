"""
Tests für shadcn/ui Chart Theme

Testet alle Funktionen des Chart-Styling-Systems.
"""

import pytest
import plotly.graph_objects as go
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
    add_chart_annotations,
    _hex_to_rgba,
    _is_dark_mode,
    _create_colorscale
)


@pytest.fixture
def theme_manager():
    """Erstellt ThemeManager für Tests"""
    tm = ThemeManager()
    tm.set_theme('shadcn-default')
    return tm


@pytest.fixture
def dark_theme_manager():
    """Erstellt ThemeManager mit Dark Theme"""
    tm = ThemeManager()
    tm.set_theme('shadcn-dark')
    return tm


@pytest.fixture
def sample_figure():
    """Erstellt einfache Test-Figure"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name="Test"))
    return fig


class TestApplyChartTheme:
    """Tests für apply_chart_theme()"""
    
    def test_applies_theme_to_figure(self, theme_manager, sample_figure):
        """Test: Theme wird auf Figure angewendet"""
        fig = apply_chart_theme(sample_figure, theme_manager)
        
        # Prüfe Layout-Updates
        assert fig.layout.font.family == theme_manager.current_theme.typography.font_family
        assert fig.layout.plot_bgcolor == theme_manager.current_theme.colors.background
        assert fig.layout.paper_bgcolor == theme_manager.current_theme.colors.background
    
    def test_applies_spline_curves(self, theme_manager, sample_figure):
        """Test: Spline-Kurven werden aktiviert"""
        fig = apply_chart_theme(sample_figure, theme_manager, enable_spline=True)
        
        # Prüfe Trace-Updates
        assert fig.data[0].line.shape == 'spline'
    
    def test_disables_spline_curves(self, theme_manager, sample_figure):
        """Test: Spline-Kurven können deaktiviert werden"""
        fig = apply_chart_theme(sample_figure, theme_manager, enable_spline=False)
        
        assert fig.data[0].line.shape == 'linear'
    
    def test_applies_gradient_fills(self, theme_manager):
        """Test: Gradient-Fills für Area-Charts"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3],
            y=[4, 5, 6],
            fill='tozeroy'
        ))
        
        fig = apply_chart_theme(fig, theme_manager, enable_gradients=True)
        
        # Prüfe dass fillcolor gesetzt wurde
        assert fig.data[0].fillcolor is not None
        assert 'rgba' in fig.data[0].fillcolor
    
    def test_styles_bar_charts(self, theme_manager):
        """Test: Bar-Charts werden gestyled"""
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3]))
        
        fig = apply_chart_theme(fig, theme_manager)
        
        # Prüfe Marker-Farbe
        assert fig.data[0].marker.color is not None
    
    def test_styles_pie_charts(self, theme_manager):
        """Test: Pie-Charts werden gestyled"""
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=['A', 'B', 'C'], values=[1, 2, 3]))
        
        fig = apply_chart_theme(fig, theme_manager)
        
        # Prüfe Marker-Colors
        assert fig.data[0].marker.colors is not None
    
    def test_detects_dark_mode(self, dark_theme_manager, sample_figure):
        """Test: Dark Mode wird automatisch erkannt"""
        fig = apply_chart_theme(sample_figure, dark_theme_manager)
        
        # Dark Theme sollte dunklen Hintergrund haben
        assert fig.layout.plot_bgcolor != '#ffffff'
    
    def test_uses_chart_colors(self, theme_manager, sample_figure):
        """Test: Chart-Farben aus Theme werden verwendet"""
        fig = apply_chart_theme(sample_figure, theme_manager)
        
        colors = get_chart_colors(theme_manager)
        assert fig.data[0].line.color == colors[0]
    
    def test_handles_multiple_traces(self, theme_manager):
        """Test: Mehrere Traces werden korrekt gestyled"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name="A"))
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[7, 8, 9], name="B"))
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[10, 11, 12], name="C"))
        
        fig = apply_chart_theme(fig, theme_manager)
        
        colors = get_chart_colors(theme_manager)
        
        # Prüfe dass verschiedene Farben verwendet werden
        assert fig.data[0].line.color == colors[0]
        assert fig.data[1].line.color == colors[1]
        assert fig.data[2].line.color == colors[2]
    
    def test_raises_error_without_theme(self, sample_figure):
        """Test: Fehler wenn kein Theme aktiv"""
        tm = ThemeManager()
        # Kein Theme gesetzt
        
        with pytest.raises(ValueError, match="Kein Theme aktiv"):
            apply_chart_theme(sample_figure, tm)


class TestHelperFunctions:
    """Tests für Helper-Funktionen"""
    
    def test_create_line_chart(self, theme_manager):
        """Test: Linien-Chart erstellen"""
        fig = create_line_chart(
            x=[1, 2, 3],
            y=[4, 5, 6],
            name="Test",
            theme_manager=theme_manager
        )
        
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatter'
        assert fig.data[0].mode == 'lines+markers'
    
    def test_create_area_chart(self, theme_manager):
        """Test: Area-Chart erstellen"""
        fig = create_area_chart(
            x=[1, 2, 3],
            y=[4, 5, 6],
            name="Test",
            theme_manager=theme_manager
        )
        
        assert len(fig.data) == 1
        assert fig.data[0].fill == 'tozeroy'
    
    def test_create_bar_chart(self, theme_manager):
        """Test: Bar-Chart erstellen"""
        fig = create_bar_chart(
            x=['A', 'B', 'C'],
            y=[1, 2, 3],
            name="Test",
            theme_manager=theme_manager
        )
        
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'
    
    def test_create_pie_chart(self, theme_manager):
        """Test: Pie-Chart erstellen"""
        fig = create_pie_chart(
            labels=['A', 'B', 'C'],
            values=[1, 2, 3],
            theme_manager=theme_manager
        )
        
        assert len(fig.data) == 1
        assert fig.data[0].type == 'pie'
    
    def test_create_themed_figure(self, theme_manager):
        """Test: Themed Figure erstellen"""
        fig = create_themed_figure(
            theme_manager=theme_manager,
            title="Test Chart"
        )
        
        assert fig.layout.title.text == "Test Chart"
        assert fig.layout.font.family == theme_manager.current_theme.typography.font_family
    
    def test_get_chart_colors(self, theme_manager):
        """Test: Chart-Farben abrufen"""
        colors = get_chart_colors(theme_manager)
        
        assert len(colors) == 5
        assert all(color.startswith('#') for color in colors)
    
    def test_apply_responsive_layout_desktop(self, sample_figure):
        """Test: Desktop-Layout"""
        fig = apply_responsive_layout(sample_figure, mobile=False)
        
        assert fig.layout.margin.l == 70
        assert fig.layout.font.size == 14
    
    def test_apply_responsive_layout_mobile(self, sample_figure):
        """Test: Mobile-Layout"""
        fig = apply_responsive_layout(sample_figure, mobile=True)
        
        assert fig.layout.margin.l == 40
        assert fig.layout.font.size == 12
        assert fig.layout.legend.orientation == 'h'
    
    def test_set_chart_title(self, theme_manager, sample_figure):
        """Test: Chart-Titel setzen"""
        fig = set_chart_title(
            sample_figure,
            "Main Title",
            "Subtitle",
            theme_manager
        )
        
        assert "Main Title" in fig.layout.title.text
        assert "Subtitle" in fig.layout.title.text
    
    def test_add_chart_annotations(self, theme_manager, sample_figure):
        """Test: Annotationen hinzufügen"""
        annotations = [
            dict(x=1, y=4, text="Point A"),
            dict(x=2, y=5, text="Point B")
        ]
        
        fig = add_chart_annotations(sample_figure, annotations, theme_manager)
        
        assert len(fig.layout.annotations) == 2
        assert fig.layout.annotations[0].text == "Point A"


class TestUtilityFunctions:
    """Tests für Utility-Funktionen"""
    
    def test_hex_to_rgba(self):
        """Test: Hex zu RGBA Konvertierung"""
        rgba = _hex_to_rgba('#38bdf8', 0.5)
        
        assert rgba == 'rgba(56, 189, 248, 0.5)'
    
    def test_hex_to_rgba_without_hash(self):
        """Test: Hex ohne # wird verarbeitet"""
        rgba = _hex_to_rgba('38bdf8', 0.5)
        
        assert rgba == 'rgba(56, 189, 248, 0.5)'
    
    def test_hex_to_rgba_full_opacity(self):
        """Test: Volle Deckkraft"""
        rgba = _hex_to_rgba('#38bdf8', 1.0)
        
        assert rgba == 'rgba(56, 189, 248, 1.0)'
    
    def test_is_dark_mode_light_theme(self, theme_manager):
        """Test: Light Theme wird erkannt"""
        is_dark = _is_dark_mode(theme_manager.current_theme)
        
        assert is_dark is False
    
    def test_is_dark_mode_dark_theme(self, dark_theme_manager):
        """Test: Dark Theme wird erkannt"""
        is_dark = _is_dark_mode(dark_theme_manager.current_theme)
        
        assert is_dark is True
    
    def test_create_colorscale(self):
        """Test: Colorscale erstellen"""
        colors = ['#ff0000', '#00ff00', '#0000ff']
        colorscale = _create_colorscale(colors)
        
        assert len(colorscale) == 3
        assert colorscale[0] == [0, '#ff0000']
        assert colorscale[1] == [0.5, '#00ff00']
        assert colorscale[2] == [1, '#0000ff']
    
    def test_create_colorscale_empty(self):
        """Test: Leere Colorscale"""
        colorscale = _create_colorscale([])
        
        assert len(colorscale) == 2
        assert colorscale[0][0] == 0
        assert colorscale[1][0] == 1


class TestIntegration:
    """Integrationstests"""
    
    def test_full_workflow(self, theme_manager):
        """Test: Kompletter Workflow"""
        # Chart erstellen
        fig = create_line_chart(
            x=[1, 2, 3, 4, 5],
            y=[10, 20, 15, 25, 30],
            name="Sales",
            theme_manager=theme_manager
        )
        
        # Titel setzen
        fig = set_chart_title(fig, "Sales Report", "Q1 2024", theme_manager)
        
        # Annotationen hinzufügen
        annotations = [dict(x=5, y=30, text="Peak")]
        fig = add_chart_annotations(fig, annotations, theme_manager)
        
        # Responsive Layout
        fig = apply_responsive_layout(fig, mobile=False)
        
        # Prüfe dass alles angewendet wurde
        assert fig.layout.title.text is not None
        assert len(fig.layout.annotations) == 1
        assert fig.data[0].line.shape == 'spline'
    
    def test_theme_switching(self, theme_manager):
        """Test: Theme-Wechsel"""
        # Erstelle Chart mit Default-Theme
        fig = create_line_chart(
            x=[1, 2, 3],
            y=[4, 5, 6],
            theme_manager=theme_manager
        )
        
        default_color = fig.data[0].line.color
        
        # Wechsle Theme
        theme_manager.set_theme('shadcn-ocean')
        
        # Wende neues Theme an
        fig = apply_chart_theme(fig, theme_manager)
        
        ocean_color = fig.data[0].line.color
        
        # Farben sollten unterschiedlich sein
        assert default_color != ocean_color
    
    def test_multiple_chart_types(self, theme_manager):
        """Test: Verschiedene Chart-Typen"""
        # Kombinierter Chart
        fig = go.Figure()
        
        # Bar
        fig.add_trace(go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3], name="Bar"))
        
        # Line
        fig.add_trace(go.Scatter(x=['A', 'B', 'C'], y=[2, 3, 4], name="Line"))
        
        # Area
        fig.add_trace(go.Scatter(
            x=['A', 'B', 'C'],
            y=[3, 4, 5],
            name="Area",
            fill='tozeroy'
        ))
        
        # Theme anwenden
        fig = apply_chart_theme(fig, theme_manager)
        
        # Prüfe dass alle Traces gestyled wurden
        assert fig.data[0].marker.color is not None  # Bar
        assert fig.data[1].line.color is not None    # Line
        assert fig.data[2].fillcolor is not None     # Area


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
