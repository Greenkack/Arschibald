"""
Tests for PDF Chart Service
"""

import pytest
from backend.services.pdf_chart_service import (
    PDFChartService,
    ChartType,
    ColorScheme
)


class TestPDFChartService:
    """Test PDF Chart Service"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return PDFChartService()
    
    @pytest.fixture
    def sample_pie_data(self):
        """Sample data for pie chart"""
        return {
            'labels': ['Solar', 'Wind', 'Hydro', 'Biomass'],
            'values': [45, 25, 20, 10]
        }
    
    @pytest.fixture
    def sample_bar_data(self):
        """Sample data for bar chart"""
        return {
            'categories': ['Jan', 'Feb', 'Mar', 'Apr'],
            'series': [[100, 150, 120, 180]]
        }
    
    @pytest.fixture
    def sample_line_data(self):
        """Sample data for line chart"""
        return {
            'categories': ['Q1', 'Q2', 'Q3', 'Q4'],
            'series': [[100, 150, 120, 180], [80, 120, 140, 160]],
            'series_names': ['Series 1', 'Series 2']
        }
    
    def test_german_number_formatting(self, service):
        """Test German number formatting"""
        assert service.format_german_number(1234.56, 2) == "1.234,56"
        assert service.format_german_number(1000000, 0) == "1.000.000"
        assert service.format_german_number(0.5, 1) == "0,5"
    
    def test_currency_formatting(self, service):
        """Test currency formatting"""
        assert service.format_currency(16999.00) == "16.999,00 €"
        assert service.format_currency(1234.56) == "1.234,56 €"
    
    def test_percentage_formatting(self, service):
        """Test percentage formatting"""
        assert service.format_percentage(85.5) == "85,5%"
        assert service.format_percentage(100.0) == "100,0%"
    
    def test_kwh_formatting(self, service):
        """Test kWh formatting"""
        assert service.format_kwh(12500) == "12.500 kWh"
        assert service.format_kwh(1234.56) == "1.235 kWh"

    
    def test_generate_pie_chart(self, service, sample_pie_data):
        """Test pie chart generation"""
        drawing = service.generate_chart(
            ChartType.PIE,
            sample_pie_data,
            width=400,
            height=300,
            color_scheme=ColorScheme.PROFESSIONAL,
            title="Energy Sources"
        )
        
        assert drawing is not None
        assert drawing.width == 400
        assert drawing.height == 300
    
    def test_generate_donut_chart(self, service, sample_pie_data):
        """Test donut chart generation"""
        drawing = service.generate_chart(
            ChartType.DONUT,
            sample_pie_data,
            width=400,
            height=300,
            color_scheme=ColorScheme.SOLAR
        )
        
        assert drawing is not None
    
    def test_generate_bar_chart(self, service, sample_bar_data):
        """Test bar chart generation"""
        drawing = service.generate_chart(
            ChartType.BAR,
            sample_bar_data,
            width=400,
            height=300,
            color_scheme=ColorScheme.NATURE,
            title="Monthly Production",
            x_label="Production (kWh)",
            y_label="Month"
        )
        
        assert drawing is not None
    
    def test_generate_column_chart(self, service, sample_bar_data):
        """Test column chart generation"""
        drawing = service.generate_chart(
            ChartType.COLUMN,
            sample_bar_data,
            width=400,
            height=300,
            color_scheme=ColorScheme.VIBRANT
        )
        
        assert drawing is not None
    
    def test_generate_line_chart(self, service, sample_line_data):
        """Test line chart generation"""
        drawing = service.generate_chart(
            ChartType.LINE,
            sample_line_data,
            width=400,
            height=300,
            color_scheme=ColorScheme.PROFESSIONAL,
            show_legend=True
        )
        
        assert drawing is not None
    
    def test_generate_area_chart(self, service, sample_line_data):
        """Test area chart generation"""
        drawing = service.generate_chart(
            ChartType.AREA,
            sample_line_data,
            width=400,
            height=300,
            color_scheme=ColorScheme.SOLAR
        )
        
        assert drawing is not None
    
    def test_generate_circle_chart(self, service):
        """Test circle chart generation"""
        data = {
            'value': 75,
            'max_value': 100,
            'label': 'Efficiency'
        }
        
        drawing = service.generate_chart(
            ChartType.CIRCLE,
            data,
            width=300,
            height=300,
            color_scheme=ColorScheme.NATURE
        )
        
        assert drawing is not None
    
    def test_generate_polar_chart(self, service):
        """Test polar chart generation"""
        data = {
            'categories': ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],
            'values': [80, 70, 60, 75, 90, 85, 65, 70]
        }
        
        drawing = service.generate_chart(
            ChartType.POLAR,
            data,
            width=400,
            height=400,
            color_scheme=ColorScheme.PROFESSIONAL
        )
        
        assert drawing is not None
    
    def test_generate_radar_chart(self, service):
        """Test radar chart generation"""
        data = {
            'categories': ['Speed', 'Power', 'Efficiency', 'Cost', 'Reliability'],
            'series': [[80, 70, 90, 60, 85], [70, 85, 75, 80, 70]],
            'series_names': ['Product A', 'Product B']
        }
        
        drawing = service.generate_chart(
            ChartType.RADAR,
            data,
            width=400,
            height=400,
            color_scheme=ColorScheme.VIBRANT,
            show_legend=True
        )
        
        assert drawing is not None
    
    def test_generate_waterfall_chart(self, service):
        """Test waterfall chart generation"""
        data = {
            'categories': ['Start', 'Income', 'Expenses', 'Taxes', 'End'],
            'values': [1000, 500, -300, -100, 0]
        }
        
        drawing = service.generate_chart(
            ChartType.WATERFALL,
            data,
            width=400,
            height=300,
            color_scheme=ColorScheme.PROFESSIONAL,
            show_values=True
        )
        
        assert drawing is not None
    
    def test_3d_effects(self, service, sample_pie_data):
        """Test 3D effects on charts"""
        drawing = service.generate_chart(
            ChartType.PIE,
            sample_pie_data,
            width=400,
            height=300,
            enable_3d=True
        )
        
        assert drawing is not None
    
    def test_all_color_schemes(self, service, sample_pie_data):
        """Test all color schemes"""
        for scheme in ColorScheme:
            drawing = service.generate_chart(
                ChartType.PIE,
                sample_pie_data,
                width=400,
                height=300,
                color_scheme=scheme
            )
            assert drawing is not None
    
    def test_generate_pdf_bytes(self, service, sample_pie_data):
        """Test PDF bytes generation"""
        pdf_bytes = service.generate_chart_pdf_bytes(
            ChartType.PIE,
            sample_pie_data,
            width=400,
            height=300
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_invalid_chart_type(self, service):
        """Test invalid chart type handling"""
        with pytest.raises(ValueError):
            service.generate_chart(
                "invalid_type",
                {},
                width=400,
                height=300
            )
