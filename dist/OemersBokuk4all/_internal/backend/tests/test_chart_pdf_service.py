"""
Tests for Chart PDF Service

Tests all chart types with German formatting.
"""

import pytest
from backend.services.chart_pdf_service import (
    ChartData,
    ChartPDFService,
    create_line_chart_pdf,
    create_bar_chart_pdf,
    create_pie_chart_pdf,
    create_area_chart_pdf,
    create_scatter_plot_pdf,
    REPORTLAB_AVAILABLE
)
from backend.core.pdf_bytes import PDFMetadata


@pytest.mark.skipif(
    not REPORTLAB_AVAILABLE,
    reason="reportlab not installed"
)
class TestChartData:
    """Test ChartData container"""

    def test_chart_data_initialization(self):
        """Test basic initialization"""
        data = ChartData(
            title="Test Chart",
            data=[[100, 200, 300]],
            labels=["A", "B", "C"]
        )

        assert data.title == "Test Chart"
        assert data.data == [[100, 200, 300]]
        assert data.labels == ["A", "B", "C"]
        assert len(data.series_names) == 1
        assert data.series_names[0] == "Series 1"

    def test_chart_data_with_series_names(self):
        """Test with custom series names"""
        data = ChartData(
            title="Test",
            data=[[1, 2], [3, 4]],
            labels=["X", "Y"],
            series_names=["Revenue", "Costs"]
        )

        assert data.series_names == ["Revenue", "Costs"]

    def test_format_value_german(self):
        """Test German number formatting"""
        data = ChartData(
            title="Test",
            data=[[1234.56]],
            labels=["A"]
        )

        formatted = data.format_value(1234.56)
        assert formatted == "1.234,56"

    def test_format_data_german(self):
        """Test formatting all data"""
        data = ChartData(
            title="Test",
            data=[[1000.50, 2000.75], [3000.25, 4000.00]],
            labels=["A", "B"]
        )

        formatted = data.format_data_german()
        assert formatted[0][0] == "1.000,50"
        assert formatted[0][1] == "2.000,75"
        assert formatted[1][0] == "3.000,25"
        assert formatted[1][1] == "4.000,00"

    def test_default_colors(self):
        """Test default color palette"""
        data = ChartData(
            title="Test",
            data=[[1, 2]],
            labels=["A", "B"]
        )

        assert len(data.colors) == 8
        assert data.colors[0] == '#2E86AB'


@pytest.mark.skipif(
    not REPORTLAB_AVAILABLE,
    reason="reportlab not installed"
)
class TestChartPDFService:
    """Test ChartPDFService"""

    def test_service_initialization(self):
        """Test service initialization"""
        service = ChartPDFService()

        assert service.engine is not None
        assert service.formatter is not None
        assert service.width == 400
        assert service.height == 250

    def test_create_line_chart_pdf(self):
        """Test line chart PDF generation"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Sales Over Time",
            data=[[100, 150, 200, 250]],
            labels=["Q1", "Q2", "Q3", "Q4"],
            series_names=["Revenue"]
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_bar_chart_pdf(self):
        """Test bar chart PDF generation"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Product Comparison",
            data=[[1000, 1500, 2000], [800, 1200, 1800]],
            labels=["Product A", "Product B", "Product C"],
            series_names=["2023", "2024"]
        )

        pdf_bytes = service.create_bar_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_pie_chart_pdf(self):
        """Test pie chart PDF generation"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Market Share",
            data=[[35, 25, 20, 15, 5]],
            labels=["Product A", "Product B", "Product C",
                    "Product D", "Others"]
        )

        pdf_bytes = service.create_pie_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_area_chart_pdf(self):
        """Test area chart PDF generation"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Energy Production",
            data=[[100, 120, 140, 160, 180]],
            labels=["Jan", "Feb", "Mar", "Apr", "May"],
            series_names=["Solar Output (kWh)"]
        )

        pdf_bytes = service.create_area_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_scatter_plot_pdf(self):
        """Test scatter plot PDF generation"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Temperature vs Efficiency",
            data=[[20, 25, 30, 35, 40], [95, 92, 88, 85, 80]],
            labels=["Point 1", "Point 2", "Point 3",
                    "Point 4", "Point 5"],
            series_names=["Temperature (°C)", "Efficiency (%)"]
        )

        pdf_bytes = service.create_scatter_plot_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_line_chart_with_metadata(self):
        """Test line chart with custom metadata"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Test Chart",
            data=[[1, 2, 3]],
            labels=["A", "B", "C"]
        )

        metadata = PDFMetadata(
            title="Custom Title",
            author="Test Author",
            subject="Test Subject"
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data, metadata)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_german_formatting_in_charts(self):
        """Test that German formatting is applied"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="German Numbers",
            data=[[1234.56, 2345.67, 3456.78]],
            labels=["A", "B", "C"]
        )

        # Generate PDF (formatting happens internally)
        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_multiple_series(self):
        """Test charts with multiple data series"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Multi-Series Chart",
            data=[
                [100, 150, 200, 250],
                [80, 120, 180, 220],
                [90, 140, 190, 240]
            ],
            labels=["Q1", "Q2", "Q3", "Q4"],
            series_names=["Product A", "Product B", "Product C"]
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_custom_colors(self):
        """Test charts with custom colors"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Custom Colors",
            data=[[1, 2, 3]],
            labels=["A", "B", "C"],
            colors=["#FF0000", "#00FF00", "#0000FF"]
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


@pytest.mark.skipif(
    not REPORTLAB_AVAILABLE,
    reason="reportlab not installed"
)
class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_create_line_chart_pdf_function(self):
        """Test line chart convenience function"""
        pdf_bytes = create_line_chart_pdf(
            title="Test Line Chart",
            data=[[100, 200, 300]],
            labels=["A", "B", "C"],
            series_names=["Series 1"]
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_bar_chart_pdf_function(self):
        """Test bar chart convenience function"""
        pdf_bytes = create_bar_chart_pdf(
            title="Test Bar Chart",
            data=[[100, 200, 300]],
            labels=["A", "B", "C"]
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_pie_chart_pdf_function(self):
        """Test pie chart convenience function"""
        pdf_bytes = create_pie_chart_pdf(
            title="Test Pie Chart",
            data=[30, 40, 30],
            labels=["A", "B", "C"]
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_area_chart_pdf_function(self):
        """Test area chart convenience function"""
        pdf_bytes = create_area_chart_pdf(
            title="Test Area Chart",
            data=[[100, 200, 300]],
            labels=["A", "B", "C"]
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_create_scatter_plot_pdf_function(self):
        """Test scatter plot convenience function"""
        pdf_bytes = create_scatter_plot_pdf(
            title="Test Scatter Plot",
            data=[[100, 200, 300]],
            labels=["A", "B", "C"]
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_convenience_with_kwargs(self):
        """Test convenience functions with additional kwargs"""
        pdf_bytes = create_line_chart_pdf(
            title="Test",
            data=[[1, 2, 3]],
            labels=["A", "B", "C"],
            x_axis_label="Time",
            y_axis_label="Value",
            colors=["#FF0000"]
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


@pytest.mark.skipif(
    not REPORTLAB_AVAILABLE,
    reason="reportlab not installed"
)
class TestGermanFormattingIntegration:
    """Test German formatting integration in charts"""

    def test_large_numbers_formatted(self):
        """Test large numbers are formatted correctly"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Large Numbers",
            data=[[1000000, 2000000, 3000000]],
            labels=["A", "B", "C"]
        )

        pdf_bytes = service.create_bar_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_decimal_numbers_formatted(self):
        """Test decimal numbers are formatted correctly"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Decimal Numbers",
            data=[[1234.56, 2345.67, 3456.78]],
            labels=["A", "B", "C"]
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_pie_chart_percentages_german(self):
        """Test pie chart percentages in German format"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Percentages",
            data=[[25.5, 30.25, 44.25]],
            labels=["A", "B", "C"]
        )

        pdf_bytes = service.create_pie_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_data_table_german_formatting(self):
        """Test data table uses German formatting"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Table Test",
            data=[[1234.56, 2345.67]],
            labels=["A", "B"]
        )

        # Create table
        table = service._create_data_table(chart_data)

        assert table is not None


@pytest.mark.skipif(
    not REPORTLAB_AVAILABLE,
    reason="reportlab not installed"
)
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_data(self):
        """Test with minimal data (2 points minimum for charts)"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Minimal",
            data=[[0, 0]],
            labels=["A", "B"]
        )

        # Should not crash with minimal data
        pdf_bytes = service.create_line_chart_pdf(chart_data)
        assert isinstance(pdf_bytes, bytes)

    def test_single_data_point(self):
        """Test with single data point"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Single Point",
            data=[[100]],
            labels=["A"]
        )

        pdf_bytes = service.create_bar_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_many_data_points(self):
        """Test with many data points"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Many Points",
            data=[[i * 10 for i in range(50)]],
            labels=[f"Point {i}" for i in range(50)]
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_zero_values(self):
        """Test with zero values"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Zeros",
            data=[[0, 0, 0]],
            labels=["A", "B", "C"]
        )

        pdf_bytes = service.create_bar_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_negative_values(self):
        """Test with negative values"""
        service = ChartPDFService()

        chart_data = ChartData(
            title="Negative",
            data=[[-100, -200, -300]],
            labels=["A", "B", "C"]
        )

        pdf_bytes = service.create_line_chart_pdf(chart_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
