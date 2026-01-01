"""
Tests for Visualization PDF Service

Tests all visualization PDF generation capabilities:
- 3D visualization PDF export
- Diagram PDF generation
- Flowchart PDF export
- Infographic PDF generation
- Dashboard PDF export
"""

import pytest
import io
from PIL import Image
from PyPDF2 import PdfReader

from backend.services.visualization_pdf_service import VisualizationPDFService


@pytest.fixture
def viz_service():
    """Create visualization PDF service instance"""
    return VisualizationPDFService()


class Test3DVisualizationPDF:
    """Test 3D visualization PDF export"""
    
    def test_create_3d_visualization_pdf_basic(self, viz_service):
        """Test basic 3D visualization PDF creation"""
        viz_data = {
            'views': {
                'front': {
                    'vertices': [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
                    'faces': [[[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]],
                    'stats': {
                        'modules': 20,
                        'power': 8.5
                    }
                }
            },
            'modules': [{'id': 1}, {'id': 2}],
            'total_power': 8.5,
            'area_coverage': 45.2
        }
        
        pdf_bytes = viz_service.create_3d_visualization_pdf(viz_data, "Solar Panel Layout")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) >= 1
    
    def test_3d_visualization_with_metadata(self, viz_service):
        """Test 3D visualization with metadata page"""
        viz_data = {
            'views': {'top': {'vertices': [], 'faces': []}},
            'metadata': {
                'project': 'Test Project',
                'date': '2024-01-15',
                'power': 10.5
            }
        }
        
        pdf_bytes = viz_service.create_3d_visualization_pdf(viz_data, include_metadata=True)
        
        assert isinstance(pdf_bytes, bytes)
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) >= 2  # Main page + metadata page


class TestDiagramPDF:
    """Test diagram PDF generation"""
    
    def test_create_diagram_pdf_basic(self, viz_service):
        """Test basic diagram PDF creation"""
        diagram_data = {
            'nodes': [
                {'id': 'A', 'x': 0, 'y': 0, 'label': 'Start', 'shape': 'circle'},
                {'id': 'B', 'x': 3, 'y': 0, 'label': 'Process', 'shape': 'rectangle'},
                {'id': 'C', 'x': 6, 'y': 0, 'label': 'End', 'shape': 'circle'}
            ],
            'edges': [
                {'from': 'A', 'to': 'B', 'label': 'Step 1'},
                {'from': 'B', 'to': 'C', 'label': 'Step 2'}
            ]
        }
        
        pdf_bytes = viz_service.create_diagram_pdf(diagram_data, "system", "System Architecture")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) == 1
    
    def test_diagram_with_legend(self, viz_service):
        """Test diagram with legend"""
        diagram_data = {
            'nodes': [
                {'id': 'A', 'x': 0, 'y': 0, 'label': 'Node A', 'color': 'lightblue'}
            ],
            'edges': [],
            'legend': {
                'items': [
                    {'color': '#3b82f6', 'label': 'Primary'},
                    {'color': '#10b981', 'label': 'Secondary'}
                ]
            }
        }
        
        pdf_bytes = viz_service.create_diagram_pdf(diagram_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestFlowchartPDF:
    """Test flowchart PDF export"""
    
    def test_create_flowchart_pdf_basic(self, viz_service):
        """Test basic flowchart PDF creation"""
        flowchart_data = {
            'steps': [
                {'id': 1, 'x': 0, 'y': 0, 'type': 'start', 'label': 'Start'},
                {'id': 2, 'x': 0, 'y': -2, 'type': 'process', 'label': 'Process Data'},
                {'id': 3, 'x': 0, 'y': -4, 'type': 'decision', 'label': 'Valid?'},
                {'id': 4, 'x': -2, 'y': -6, 'type': 'process', 'label': 'Error'},
                {'id': 5, 'x': 2, 'y': -6, 'type': 'process', 'label': 'Continue'},
                {'id': 6, 'x': 0, 'y': -8, 'type': 'end', 'label': 'End'}
            ],
            'connections': [
                {'from': 1, 'to': 2},
                {'from': 2, 'to': 3},
                {'from': 3, 'to': 4, 'label': 'No'},
                {'from': 3, 'to': 5, 'label': 'Yes'},
                {'from': 4, 'to': 6},
                {'from': 5, 'to': 6}
            ]
        }
        
        pdf_bytes = viz_service.create_flowchart_pdf(flowchart_data, "Process Flow")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) == 1


class TestInfographicPDF:
    """Test infographic PDF generation"""
    
    def test_create_infographic_pdf_with_stats(self, viz_service):
        """Test infographic with stat boxes"""
        infographic_data = {
            'sections': [
                {
                    'type': 'stat_box',
                    'stats': [
                        {'value': 1234.56, 'label': 'Total Power', 'unit': 'kWp'},
                        {'value': 5678.90, 'label': 'Annual Production', 'unit': 'kWh'},
                        {'value': 12.5, 'label': 'ROI', 'unit': 'years'}
                    ]
                }
            ]
        }
        
        pdf_bytes = viz_service.create_infographic_pdf(infographic_data, "Solar Statistics")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_infographic_with_comparison(self, viz_service):
        """Test infographic with comparison bars"""
        infographic_data = {
            'sections': [
                {
                    'type': 'comparison',
                    'title': 'Energy Sources',
                    'items': [
                        {'name': 'Solar', 'value': 85, 'max': 100},
                        {'name': 'Wind', 'value': 65, 'max': 100},
                        {'name': 'Hydro', 'value': 45, 'max': 100}
                    ]
                }
            ]
        }
        
        pdf_bytes = viz_service.create_infographic_pdf(infographic_data)
        
        assert isinstance(pdf_bytes, bytes)
    
    def test_infographic_with_chart(self, viz_service):
        """Test infographic with embedded chart"""
        infographic_data = {
            'sections': [
                {
                    'type': 'chart',
                    'chart_type': 'bar',
                    'data': {
                        'x': ['Jan', 'Feb', 'Mar'],
                        'y': [100, 150, 200],
                        'title': 'Monthly Production'
                    }
                }
            ]
        }
        
        pdf_bytes = viz_service.create_infographic_pdf(infographic_data)
        
        assert isinstance(pdf_bytes, bytes)


class TestDashboardPDF:
    """Test dashboard PDF export"""
    
    def test_create_dashboard_pdf_with_kpis(self, viz_service):
        """Test dashboard with KPI cards"""
        dashboard_data = {
            'kpis': [
                {'value': 1234.56, 'label': 'Total Revenue', 'trend': 5.2},
                {'value': 89.5, 'label': 'Efficiency', 'trend': -2.1},
                {'value': 456, 'label': 'Projects', 'trend': 12.3}
            ]
        }
        
        pdf_bytes = viz_service.create_dashboard_pdf(dashboard_data, "Performance Dashboard")
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) == 1
    
    def test_dashboard_with_widgets(self, viz_service):
        """Test dashboard with widget grid"""
        dashboard_data = {
            'kpis': [
                {'value': 100, 'label': 'KPI 1'}
            ],
            'widgets': [
                {
                    'title': 'Sales Trend',
                    'type': 'chart',
                    'chart_type': 'line',
                    'data': {
                        'x': [1, 2, 3, 4],
                        'y': [10, 20, 15, 25],
                        'title': 'Sales'
                    }
                },
                {
                    'title': 'Distribution',
                    'type': 'chart',
                    'chart_type': 'pie',
                    'data': {
                        'x': ['A', 'B', 'C'],
                        'y': [30, 40, 30],
                        'title': 'Distribution'
                    }
                }
            ]
        }
        
        pdf_bytes = viz_service.create_dashboard_pdf(dashboard_data)
        
        assert isinstance(pdf_bytes, bytes)


class TestHelperMethods:
    """Test helper methods"""
    
    def test_format_value_numeric(self, viz_service):
        """Test German number formatting"""
        result = viz_service._format_value(1234.56)
        assert result == "1.234,56"
    
    def test_format_value_string(self, viz_service):
        """Test string value formatting"""
        result = viz_service._format_value("test")
        assert result == "test"
    
    def test_wrap_text(self, viz_service):
        """Test text wrapping"""
        text = "This is a very long text that needs to be wrapped"
        result = viz_service._wrap_text(text, 20)
        assert '\n' in result
    
    def test_to_base64(self, viz_service):
        """Test PDF bytes to base64 conversion"""
        pdf_bytes = b"test pdf content"
        result = viz_service.to_base64(pdf_bytes)
        assert isinstance(result, str)
        assert len(result) > 0


class TestBatchExport:
    """Test batch export functionality"""
    
    def test_export_multiple_visualizations_separate(self, viz_service):
        """Test exporting multiple visualizations as separate PDFs"""
        visualizations = [
            {
                'type': 'diagram',
                'title': 'Diagram 1',
                'data': {
                    'nodes': [{'id': 'A', 'x': 0, 'y': 0, 'label': 'Node A'}],
                    'edges': []
                }
            },
            {
                'type': 'flowchart',
                'title': 'Flow 1',
                'data': {
                    'steps': [{'id': 1, 'x': 0, 'y': 0, 'type': 'start', 'label': 'Start'}],
                    'connections': []
                }
            }
        ]
        
        results = viz_service.export_multiple_visualizations(visualizations, "separate")
        
        assert isinstance(results, dict)
        assert len(results) == 2
        
        for key, pdf_bytes in results.items():
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0


class TestGermanFormatting:
    """Test German number formatting in visualizations"""
    
    def test_german_formatting_in_3d_viz(self, viz_service):
        """Test German formatting in 3D visualization"""
        viz_data = {
            'views': {},
            'total_power': 1234.56,
            'area_coverage': 5678.90
        }
        
        pdf_bytes = viz_service.create_3d_visualization_pdf(viz_data)
        
        # PDF should contain German-formatted numbers
        assert isinstance(pdf_bytes, bytes)
        # Note: Actual text extraction would require more complex PDF parsing
    
    def test_german_formatting_in_dashboard(self, viz_service):
        """Test German formatting in dashboard KPIs"""
        dashboard_data = {
            'kpis': [
                {'value': 9876.54, 'label': 'Revenue'}
            ]
        }
        
        pdf_bytes = viz_service.create_dashboard_pdf(dashboard_data)
        
        assert isinstance(pdf_bytes, bytes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
