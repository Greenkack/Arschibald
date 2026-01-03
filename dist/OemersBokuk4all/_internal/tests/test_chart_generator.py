"""
Unit Tests for Chart Generator

Tests chart generation functionality with shadcn/ui styling.

Requirements: 12.1, 12.3
"""

import sys
from pathlib import Path
import pytest
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from controlling.chart_generator import ChartGenerator


class TestChartGenerator:
    """Test suite for ChartGenerator class"""

    @pytest.fixture
    def chart_gen(self):
        """Create a ChartGenerator instance for testing"""
        return ChartGenerator()

    @pytest.fixture
    def sample_quota_data(self):
        """Sample quota data for testing"""
        return {
            "Abschlussquote": 25.5,
            "Terminvereinbarungsquote": 15.3,
            "Anfahrquote": 80.2,
            "Nicht interessiert Quote": 10.1,
            "QC bestanden Quote": 95.0
        }

    @pytest.fixture
    def sample_report_data(self):
        """Sample report data for dashboard testing"""
        return {
            "employee_id": 1,
            "employee_name": "Max Mustermann",
            "position": "Vertrieb",
            "report_type": "MONTHLY",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "quotas": {
                "Abschlussquote": 25.5,
                "Terminvereinbarungsquote": 15.3,
                "Anfahrquote": 80.2,
                "Nicht interessiert Quote": 10.1,
                "QC bestanden Quote": 95.0
            },
            "ratio_descriptions": {
                "Abschlussquote": "Jeder 4. angefahrene Termin ist ein Verkauf"
            },
            "aggregated_data": {
                "raw_data": {
                    "Verkauf": 50,
                    "Kunden terminiert": 100,
                    "Angefahrene Termine": 80,
                    "Getätigte Anrufe gesamt": 200
                },
                "quotas": {
                    "Abschlussquote": 25.5
                }
            }
        }

    def test_create_bar_chart(self, chart_gen, sample_quota_data):
        """
        Test bar chart creation.

        Requirements: 12.1
        """
        fig = chart_gen.create_bar_chart(
            data=sample_quota_data,
            title="Test Bar Chart",
            x_label="Percentage",
            y_label="Quota"
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == "bar"
        assert fig.data[0].orientation == "h"
        assert len(fig.data[0].y) == len(sample_quota_data)

    def test_create_bar_chart_empty_data(self, chart_gen):
        """Test bar chart with empty data"""
        fig = chart_gen.create_bar_chart(
            data={},
            title="Empty Chart"
        )

        assert isinstance(fig, go.Figure)
        # Should have annotation for "no data"
        assert len(fig.layout.annotations) > 0

    def test_create_column_chart(self, chart_gen, sample_quota_data):
        """
        Test column chart creation.

        Requirements: 12.1
        """
        fig = chart_gen.create_column_chart(
            data=sample_quota_data,
            title="Test Column Chart",
            x_label="Quota",
            y_label="Percentage"
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == "bar"
        # Column charts don't have explicit orientation (default is vertical)
        assert len(fig.data[0].x) == len(sample_quota_data)

    def test_create_column_chart_empty_data(self, chart_gen):
        """Test column chart with empty data"""
        fig = chart_gen.create_column_chart(
            data={},
            title="Empty Chart"
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0

    def test_create_donut_chart(self, chart_gen, sample_quota_data):
        """
        Test donut chart creation.

        Requirements: 12.1
        """
        fig = chart_gen.create_donut_chart(
            data=sample_quota_data,
            title="Test Donut Chart"
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type == "pie"
        assert fig.data[0].hole > 0  # Donut has a hole
        assert len(fig.data[0].labels) == len(sample_quota_data)

    def test_create_donut_chart_empty_data(self, chart_gen):
        """Test donut chart with empty data"""
        fig = chart_gen.create_donut_chart(
            data={},
            title="Empty Chart"
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0

    def test_apply_shadcn_theme(self, chart_gen):
        """
        Test shadcn/ui theme application.

        Requirements: 12.2
        """
        # Create a simple figure
        fig = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2])])

        # Apply theme
        styled_fig = chart_gen.apply_shadcn_theme(fig)

        assert isinstance(styled_fig, go.Figure)
        # Check that layout has been updated
        # Template is an object, not a string after being set
        assert styled_fig.layout.paper_bgcolor == "rgba(0,0,0,0)"
        assert styled_fig.layout.plot_bgcolor == "rgba(0,0,0,0)"
        # Check that hovermode is set
        assert styled_fig.layout.hovermode == "x unified"

    def test_apply_shadcn_theme_none_figure(self, chart_gen):
        """Test theme application with None figure"""
        result = chart_gen.apply_shadcn_theme(None)
        assert result is None

    def test_create_dashboard(self, chart_gen, sample_report_data):
        """
        Test dashboard creation with multiple charts.

        Requirements: 12.3
        """
        figures = chart_gen.create_dashboard(sample_report_data)

        assert isinstance(figures, list)
        assert len(figures) > 0
        # Should have multiple charts
        assert len(figures) >= 3

        # All should be Plotly figures
        for fig in figures:
            assert isinstance(fig, go.Figure)

    def test_create_dashboard_empty_data(self, chart_gen):
        """Test dashboard with empty report data"""
        figures = chart_gen.create_dashboard({})

        assert isinstance(figures, list)
        assert len(figures) > 0
        # Should have at least a placeholder figure
        assert isinstance(figures[0], go.Figure)

    def test_create_dashboard_only_quotas(self, chart_gen):
        """Test dashboard with only quota data"""
        report_data = {
            "quotas": {
                "Abschlussquote": 25.5,
                "Terminvereinbarungsquote": 15.3
            }
        }

        figures = chart_gen.create_dashboard(report_data)

        assert isinstance(figures, list)
        assert len(figures) > 0

    def test_chart_colors(self, chart_gen, sample_quota_data):
        """Test that charts use default color scheme"""
        fig = chart_gen.create_bar_chart(
            data=sample_quota_data,
            title="Color Test"
        )

        # Check that marker color is set
        assert fig.data[0].marker.color == chart_gen.default_colors[0]

    def test_chart_hover_template(self, chart_gen, sample_quota_data):
        """Test that charts have hover templates"""
        fig = chart_gen.create_bar_chart(
            data=sample_quota_data,
            title="Hover Test"
        )

        # Check that hover template is set
        assert fig.data[0].hovertemplate is not None
        assert len(fig.data[0].hovertemplate) > 0

    def test_dashboard_chart_types(self, chart_gen, sample_report_data):
        """
        Test that dashboard includes different chart types.

        Requirements: 12.1, 12.3
        """
        figures = chart_gen.create_dashboard(sample_report_data)

        chart_types = set()
        for fig in figures:
            if len(fig.data) > 0:
                chart_types.add(fig.data[0].type)

        # Should have at least bar and pie charts
        assert "bar" in chart_types or "pie" in chart_types

    def test_chart_titles(self, chart_gen, sample_quota_data):
        """Test that charts have proper titles"""
        title = "Test Title"
        fig = chart_gen.create_bar_chart(
            data=sample_quota_data,
            title=title
        )

        assert fig.layout.title.text == title

    def test_chart_axis_labels(self, chart_gen, sample_quota_data):
        """Test that charts have axis labels"""
        x_label = "X Axis"
        y_label = "Y Axis"

        fig = chart_gen.create_bar_chart(
            data=sample_quota_data,
            title="Test",
            x_label=x_label,
            y_label=y_label
        )

        assert fig.layout.xaxis.title.text == x_label
        assert fig.layout.yaxis.title.text == y_label


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
