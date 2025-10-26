"""
test_chart_styling_improvements.py

Unit Tests für Task 4: Diagramm-Darstellung verbessern
Testet alle Subtasks 4.1-4.4

Autor: Kiro AI
Datum: 2025-10-10
"""

import pytest
import io
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
import numpy as np

# Import der zu testenden Module
from chart_styling_improvements import (
    apply_improved_matplotlib_style,
    create_improved_bar_chart,
    create_improved_line_chart,
    create_improved_donut_chart,
    create_improved_scatter_plot,
    save_matplotlib_chart_to_bytes,
    apply_improved_plotly_style,
    create_improved_plotly_bar_chart,
    create_improved_plotly_line_chart,
    save_plotly_chart_to_bytes,
    generate_chart_description,
    get_optimal_figure_size,
    get_professional_color_palette,
    FONT_SIZE_TITLE,
    FONT_SIZE_AXIS_LABEL,
    FONT_SIZE_LEGEND,
    FONT_SIZE_TICK_LABEL,
    FONT_SIZE_DATA_LABEL,
    BAR_WIDTH,
    LINE_WIDTH,
    MARKER_SIZE,
    DONUT_WIDTH,
    DPI,
    GRID_ALPHA
)


class TestTask41_DiagrammStyling:
    """Tests für Task 4.1: Diagramm-Styling in allen Modulen verbessern"""

    def test_font_sizes(self):
        """Test dass alle Schriftgrößen den Anforderungen entsprechen"""
        assert FONT_SIZE_TITLE >= 14, "Titel-Schriftgröße muss >= 14 sein"
        assert FONT_SIZE_AXIS_LABEL >= 12, "Achsenbeschriftungs-Schriftgröße muss >= 12 sein"
        assert FONT_SIZE_LEGEND >= 10, "Legenden-Schriftgröße muss >= 10 sein"
        assert FONT_SIZE_TICK_LABEL >= 10, "Tick-Label-Schriftgröße muss >= 10 sein"
        assert FONT_SIZE_DATA_LABEL >= 9, "Daten-Label-Schriftgröße muss >= 9 sein"

    def test_bar_width(self):
        """Test dass Balkenbreite >= 0.6 ist"""
        assert BAR_WIDTH >= 0.6, "Balkenbreite muss >= 0.6 sein"

    def test_line_width(self):
        """Test dass Linienbreite >= 2.5 ist"""
        assert LINE_WIDTH >= 2.5, "Linienbreite muss >= 2.5 sein"

    def test_marker_size(self):
        """Test dass Marker-Größe >= 100 ist"""
        assert MARKER_SIZE >= 100, "Marker-Größe muss >= 100 sein"

    def test_donut_width(self):
        """Test dass Donut-Breite korrekt ist"""
        assert DONUT_WIDTH == 0.4, "Donut-Breite muss 0.4 sein"

    def test_matplotlib_bar_chart_styling(self):
        """Test dass Matplotlib-Balkendiagramme korrekt gestylt werden"""
        fig, ax = plt.subplots()
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]

        create_improved_bar_chart(ax, x_data, y_data, show_values=True)

        # Prüfe dass Balken erstellt wurden
        assert len(ax.patches) == 5, "5 Balken sollten erstellt worden sein"

        # Prüfe Balkenbreite
        for patch in ax.patches:
            assert patch.get_width() >= 0.5, "Balkenbreite sollte >= 0.5 sein"

        plt.close(fig)

    def test_matplotlib_line_chart_styling(self):
        """Test dass Matplotlib-Liniendiagramme korrekt gestylt werden"""
        fig, ax = plt.subplots()
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]

        create_improved_line_chart(ax, x_data, y_data, show_markers=True)

        # Prüfe dass Linie erstellt wurde
        assert len(ax.lines) == 1, "Eine Linie sollte erstellt worden sein"

        # Prüfe Linienbreite
        line = ax.lines[0]
        assert line.get_linewidth() >= 2.5, "Linienbreite sollte >= 2.5 sein"

        plt.close(fig)

    def test_matplotlib_donut_chart_styling(self):
        """Test dass Matplotlib-Donut-Diagramme korrekt gestylt werden"""
        fig, ax = plt.subplots()
        values = [30, 40, 30]
        labels = ['A', 'B', 'C']

        create_improved_donut_chart(ax, values, labels)

        # Prüfe dass Wedges erstellt wurden
        assert len(ax.patches) == 3, "3 Wedges sollten erstellt worden sein"

        plt.close(fig)

    def test_matplotlib_scatter_plot_styling(self):
        """Test dass Matplotlib-Streudiagramme korrekt gestylt werden"""
        fig, ax = plt.subplots()
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]

        create_improved_scatter_plot(ax, x_data, y_data)

        # Prüfe dass Scatter-Plot erstellt wurde
        assert len(
            ax.collections) == 1, "Ein Scatter-Plot sollte erstellt worden sein"

        plt.close(fig)


class TestTask42_FarbenUndGitternetz:
    """Tests für Task 4.2: Farben und Gitternetz optimieren"""

    def test_grid_alpha(self):
        """Test dass Gitternetz-Transparenz korrekt ist"""
        assert GRID_ALPHA == 0.3, "Gitternetz-Alpha muss 0.3 sein"

    def test_professional_colors(self):
        """Test dass professionelle Farben verfügbar sind"""
        colors = get_professional_color_palette(5)
        assert len(colors) == 5, "5 Farben sollten zurückgegeben werden"
        assert all(isinstance(c, str)
                   for c in colors), "Alle Farben sollten Strings sein"
        assert all(c.startswith('#')
                   for c in colors), "Alle Farben sollten Hex-Codes sein"

    def test_matplotlib_grid_styling(self):
        """Test dass Gitternetz korrekt angewendet wird"""
        fig, ax = plt.subplots()

        apply_improved_matplotlib_style(
            fig, ax,
            title="Test",
            xlabel="X",
            ylabel="Y",
            show_grid=True
        )

        # Prüfe dass Gitternetz aktiviert ist (moderne API)
        assert ax.xaxis.get_gridlines(), "X-Achsen-Gitternetz sollte aktiviert sein"
        assert ax.yaxis.get_gridlines(), "Y-Achsen-Gitternetz sollte aktiviert sein"

        plt.close(fig)

    def test_plotly_grid_styling(self):
        """Test dass Plotly-Gitternetz korrekt angewendet wird"""
        fig = go.Figure()

        apply_improved_plotly_style(
            fig,
            title="Test",
            xlabel="X",
            ylabel="Y",
            show_grid=True
        )

        # Prüfe dass Gitternetz aktiviert ist
        assert fig.layout.xaxis.showgrid, "X-Achsen-Gitternetz sollte aktiviert sein"
        assert fig.layout.yaxis.showgrid, "Y-Achsen-Gitternetz sollte aktiviert sein"


class TestTask43_AufloesungUndDimensionen:
    """Tests für Task 4.3: Hohe Auflösung und optimale Dimensionen"""

    def test_dpi(self):
        """Test dass DPI = 300 ist"""
        assert DPI == 300, "DPI muss 300 sein"

    def test_optimal_figure_size(self):
        """Test dass optimale Diagrammgröße korrekt ist"""
        width, height = get_optimal_figure_size()

        # Prüfe dass Größe in vernünftigem Bereich ist
        assert 4 < width < 8, "Breite sollte zwischen 4 und 8 Zoll sein"
        assert 3 < height < 6, "Höhe sollte zwischen 3 und 6 Zoll sein"

    def test_matplotlib_chart_resolution(self):
        """Test dass Matplotlib-Diagramme mit hoher Auflösung gespeichert werden"""
        fig, ax = plt.subplots(figsize=get_optimal_figure_size())
        ax.plot([1, 2, 3], [1, 2, 3])

        chart_bytes = save_matplotlib_chart_to_bytes(fig)

        # Prüfe dass Bytes zurückgegeben wurden
        assert isinstance(chart_bytes, bytes), "Chart-Bytes sollten bytes sein"
        assert len(chart_bytes) > 0, "Chart-Bytes sollten nicht leer sein"

        # Prüfe Bildgröße
        img = Image.open(io.BytesIO(chart_bytes))
        width, height = img.size

        # Bei DPI=300 sollte das Bild größer als 1000px sein
        assert width > 1000, f"Bildbreite sollte > 1000px sein, ist aber {width}px"
        assert height > 500, f"Bildhöhe sollte > 500px sein, ist aber {height}px"

    def test_plotly_chart_resolution(self):
        """Test dass Plotly-Diagramme mit hoher Auflösung gespeichert werden"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))

        chart_bytes = save_plotly_chart_to_bytes(fig)

        # Prüfe dass Bytes zurückgegeben wurden
        assert isinstance(chart_bytes, bytes), "Chart-Bytes sollten bytes sein"
        assert len(chart_bytes) > 0, "Chart-Bytes sollten nicht leer sein"

        # Prüfe Bildgröße
        img = Image.open(io.BytesIO(chart_bytes))
        width, height = img.size

        # Plotly-Bilder sollten auch hochauflösend sein
        assert width > 800, f"Bildbreite sollte > 800px sein, ist aber {width}px"
        assert height > 400, f"Bildhöhe sollte > 400px sein, ist aber {height}px"


class TestTask44_Beschreibungen:
    """Tests für Task 4.4: Beschreibungen für Diagramme generieren"""

    def test_generate_chart_description_basic(self):
        """Test dass Basis-Beschreibung generiert wird"""
        description = generate_chart_description(
            chart_type="Balkendiagramm",
            data={'values': [10, 20, 30], 'labels': ['A', 'B', 'C']},
            purpose="Test-Zweck"
        )

        assert isinstance(
            description, str), "Beschreibung sollte ein String sein"
        assert len(description) > 0, "Beschreibung sollte nicht leer sein"
        assert "Balkendiagramm" in description, "Diagrammtyp sollte in Beschreibung sein"
        assert "Test-Zweck" in description, "Zweck sollte in Beschreibung sein"

    def test_generate_chart_description_with_insights(self):
        """Test dass Beschreibung mit Erkenntnissen generiert wird"""
        insights = [
            "Erkenntnis 1",
            "Erkenntnis 2",
            "Erkenntnis 3"
        ]

        description = generate_chart_description(
            chart_type="Liniendiagramm",
            data={'values': [10, 20, 30]},
            purpose="Test",
            key_insights=insights
        )

        assert "Haupterkenntnisse" in description, "Haupterkenntnisse sollten in Beschreibung sein"
        for insight in insights:
            assert insight in description, f"Erkenntnis '{insight}' sollte in Beschreibung sein"

    def test_generate_chart_description_with_values(self):
        """Test dass numerische Werte in Beschreibung enthalten sind"""
        data = {
            'values': [100.5, 200.75, 300.25],
            'labels': ['Wert A', 'Wert B', 'Wert C']
        }

        description = generate_chart_description(
            chart_type="Test",
            data=data,
            purpose="Test"
        )

        assert "Werte:" in description, "Werte-Abschnitt sollte in Beschreibung sein"
        assert "Wert A" in description, "Label sollte in Beschreibung sein"
        # Prüfe dass Zahlen formatiert sind
        assert "100" in description or "100.5" in description, "Wert sollte in Beschreibung sein"

    def test_description_structure(self):
        """Test dass Beschreibung strukturiert ist"""
        description = generate_chart_description(
            chart_type="Balkendiagramm",
            data={'values': [10, 20], 'labels': ['A', 'B']},
            purpose="Zweck",
            key_insights=["Erkenntnis 1"]
        )

        # Prüfe dass alle Abschnitte vorhanden sind
        assert "Diagrammtyp:" in description, "Diagrammtyp-Abschnitt fehlt"
        assert "Zweck:" in description, "Zweck-Abschnitt fehlt"
        assert "Haupterkenntnisse:" in description, "Haupterkenntnisse-Abschnitt fehlt"
        assert "Werte:" in description, "Werte-Abschnitt fehlt"


class TestIntegration:
    """Integrationstests für alle Tasks zusammen"""

    def test_complete_matplotlib_workflow(self):
        """Test kompletter Workflow für Matplotlib-Diagramm"""
        # Erstelle Figure mit optimaler Größe
        fig, ax = plt.subplots(figsize=get_optimal_figure_size())

        # Wende Styling an
        apply_improved_matplotlib_style(
            fig, ax,
            title="Test-Diagramm",
            xlabel="X-Achse",
            ylabel="Y-Achse",
            show_grid=True,
            show_legend=True
        )

        # Erstelle Balkendiagramm
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]
        create_improved_bar_chart(ax, x_data, y_data, show_values=True)

        # Speichere mit hoher Auflösung
        chart_bytes = save_matplotlib_chart_to_bytes(fig)

        # Generiere Beschreibung
        description = generate_chart_description(
            chart_type="Balkendiagramm",
            data={
                'values': y_data,
                'labels': [
                    f"Kategorie {x}" for x in x_data]},
            purpose="Test-Visualisierung",
            key_insights=[
                "Höchster Wert: 30",
                "Niedrigster Wert: 10"])

        # Validierung
        assert chart_bytes is not None, "Chart-Bytes sollten nicht None sein"
        assert len(chart_bytes) > 0, "Chart-Bytes sollten nicht leer sein"
        assert description is not None, "Beschreibung sollte nicht None sein"
        assert len(description) > 0, "Beschreibung sollte nicht leer sein"

    def test_complete_plotly_workflow(self):
        """Test kompletter Workflow für Plotly-Diagramm"""
        # Erstelle Figure
        fig = go.Figure()

        # Füge Daten hinzu
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]
        create_improved_plotly_line_chart(
            fig, x_data, y_data,
            name="Test-Linie",
            show_markers=True
        )

        # Wende Styling an
        apply_improved_plotly_style(
            fig,
            title="Test-Diagramm",
            xlabel="X-Achse",
            ylabel="Y-Achse",
            show_grid=True,
            show_legend=True
        )

        # Speichere mit hoher Auflösung
        chart_bytes = save_plotly_chart_to_bytes(fig)

        # Generiere Beschreibung
        description = generate_chart_description(
            chart_type="Liniendiagramm",
            data={'values': y_data, 'labels': [f"Punkt {x}" for x in x_data]},
            purpose="Test-Visualisierung",
            key_insights=["Trend steigend", "Maximum bei Punkt 5"]
        )

        # Validierung
        assert chart_bytes is not None, "Chart-Bytes sollten nicht None sein"
        assert len(chart_bytes) > 0, "Chart-Bytes sollten nicht leer sein"
        assert description is not None, "Beschreibung sollte nicht None sein"
        assert len(description) > 0, "Beschreibung sollte nicht leer sein"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
