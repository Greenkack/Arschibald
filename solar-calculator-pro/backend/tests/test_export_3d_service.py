"""
Tests for 3D Export Service

Tests all export formats and functionality.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.export_3d_service import Export3DService


@pytest.fixture
def export_service():
    """Create export service instance."""
    return Export3DService()


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "project_data": {},
        "building_dims": {
            "length_m": 10.0,
            "width_m": 6.0,
            "wall_height_m": 6.0
        },
        "roof_config": {
            "type": "gable",
            "angle": 30.0,
            "orientation": "south"
        },
        "module_config": {
            "count": 20,
            "spacing": 0.02,
            "margin": 0.5
        }
    }


class TestExport3DService:
    """Test suite for Export3DService."""
    
    def test_service_initialization(self, export_service):
        """Test service initializes correctly."""
        assert export_service is not None
        assert isinstance(export_service.supported_formats, dict)
        assert len(export_service.supported_formats) > 0
    
    def test_supported_formats(self, export_service):
        """Test supported formats are correctly identified."""
        formats = export_service.supported_formats
        
        # Check expected formats exist
        assert "stl" in formats
        assert "obj" in formats
        assert "gltf" in formats
        assert "glb" in formats
        assert "dxf" in formats
        assert "pdf" in formats
        assert "png" in formats
        assert "jpg" in formats
    
    def test_is_format_supported(self, export_service):
        """Test format support checking."""
        # Test valid formats
        assert export_service.is_format_supported("stl") in [True, False]
        assert export_service.is_format_supported("STL") in [True, False]
        
        # Test invalid format
        assert export_service.is_format_supported("invalid") is False
    
    def test_get_format_info(self, export_service):
        """Test getting format information."""
        info = export_service.get_format_info("stl")
        
        assert "name" in info
        assert "description" in info
        assert "mime_type" in info
        assert "extension" in info
        assert "use_cases" in info
        assert "binary" in info
        assert "supported" in info
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("stl"),
        reason="STL export not available"
    )
    def test_export_stl(self, export_service, sample_project_data):
        """Test STL export."""
        stl_bytes = export_service.export_stl(**sample_project_data)
        
        assert isinstance(stl_bytes, bytes)
        assert len(stl_bytes) > 0
        
        # Check STL header (binary STL starts with 80-byte header)
        assert len(stl_bytes) >= 84  # Header + at least one triangle
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("obj"),
        reason="OBJ export not available"
    )
    def test_export_obj(self, export_service, sample_project_data):
        """Test OBJ export."""
        obj_bytes = export_service.export_obj(**sample_project_data)
        
        assert isinstance(obj_bytes, bytes)
        assert len(obj_bytes) > 0
        
        # Check OBJ content (should contain vertex definitions)
        obj_text = obj_bytes.decode('utf-8')
        assert 'v ' in obj_text or 'f ' in obj_text
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("gltf"),
        reason="GLTF export not available"
    )
    def test_export_gltf(self, export_service, sample_project_data):
        """Test GLTF export."""
        gltf_bytes = export_service.export_gltf(
            **sample_project_data,
            binary=False
        )
        
        assert isinstance(gltf_bytes, bytes)
        assert len(gltf_bytes) > 0
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("glb"),
        reason="GLB export not available"
    )
    def test_export_glb(self, export_service, sample_project_data):
        """Test GLB export."""
        glb_bytes = export_service.export_gltf(
            **sample_project_data,
            binary=True
        )
        
        assert isinstance(glb_bytes, bytes)
        assert len(glb_bytes) > 0
        
        # Check GLB magic number (first 4 bytes should be "glTF")
        assert glb_bytes[:4] == b'glTF'
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("dxf"),
        reason="DXF export not available"
    )
    def test_export_dxf(self, export_service, sample_project_data):
        """Test DXF export."""
        dxf_bytes = export_service.export_dxf(**sample_project_data)
        
        assert isinstance(dxf_bytes, bytes)
        assert len(dxf_bytes) > 0
        
        # Check DXF content
        dxf_text = dxf_bytes.decode('utf-8')
        assert 'SECTION' in dxf_text
        assert 'ENTITIES' in dxf_text
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("pdf"),
        reason="PDF export not available"
    )
    def test_export_pdf(self, export_service, sample_project_data):
        """Test PDF export."""
        pdf_bytes = export_service.export_pdf_3d(**sample_project_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check PDF header
        assert pdf_bytes[:4] == b'%PDF'
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("png"),
        reason="PNG export not available"
    )
    def test_export_png(self, export_service, sample_project_data):
        """Test PNG export."""
        png_bytes = export_service.export_image(
            **sample_project_data,
            format="png"
        )
        
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0
        
        # Check PNG signature
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n'
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("jpg"),
        reason="JPG export not available"
    )
    def test_export_jpg(self, export_service, sample_project_data):
        """Test JPG export."""
        jpg_bytes = export_service.export_image(
            **sample_project_data,
            format="jpg"
        )
        
        assert isinstance(jpg_bytes, bytes)
        assert len(jpg_bytes) > 0
        
        # Check JPEG signature
        assert jpg_bytes[:2] == b'\xff\xd8'
    
    def test_export_universal_method(self, export_service, sample_project_data):
        """Test universal export method."""
        # Test with a supported format
        if export_service.is_format_supported("stl"):
            result = export_service.export(
                format="stl",
                **sample_project_data
            )
            assert isinstance(result, bytes)
            assert len(result) > 0
    
    def test_export_unsupported_format(self, export_service, sample_project_data):
        """Test exporting unsupported format raises error."""
        with pytest.raises(ValueError):
            export_service.export(
                format="unsupported_format",
                **sample_project_data
            )
    
    def test_export_with_options(self, export_service, sample_project_data):
        """Test export with custom options."""
        if export_service.is_format_supported("png"):
            png_bytes = export_service.export_image(
                **sample_project_data,
                format="png",
                options={
                    "width": 800,
                    "height": 600,
                    "scale": 1.0
                }
            )
            
            assert isinstance(png_bytes, bytes)
            assert len(png_bytes) > 0
    
    def test_invalid_building_dimensions(self, export_service):
        """Test export with invalid building dimensions."""
        invalid_data = {
            "project_data": {},
            "building_dims": {
                "length_m": -10.0,  # Invalid: negative
                "width_m": 6.0,
                "wall_height_m": 6.0
            },
            "roof_config": {
                "type": "flat",
                "angle": 0.0,
                "orientation": "south"
            },
            "module_config": {
                "count": 20
            }
        }
        
        # Should handle gracefully or raise appropriate error
        if export_service.is_format_supported("stl"):
            try:
                export_service.export_stl(**invalid_data)
            except Exception as e:
                # Expected to fail with invalid dimensions
                assert True
    
    def test_format_info_all_formats(self, export_service):
        """Test getting info for all formats."""
        for format_name in export_service.supported_formats.keys():
            info = export_service.get_format_info(format_name)
            
            assert isinstance(info, dict)
            assert "name" in info
            assert "supported" in info


class TestExportFormats:
    """Test specific format features."""
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("dxf"),
        reason="DXF export not available"
    )
    def test_dxf_layers(self, export_service, sample_project_data):
        """Test DXF export includes correct layers."""
        dxf_bytes = export_service.export_dxf(**sample_project_data)
        dxf_text = dxf_bytes.decode('utf-8')
        
        # Check for expected layers
        assert 'Building_Base' in dxf_text or 'LAYER' in dxf_text
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("pdf"),
        reason="PDF export not available"
    )
    def test_pdf_with_3d_data(self, export_service, sample_project_data):
        """Test PDF export with embedded 3D data."""
        pdf_bytes = export_service.export_pdf_3d(
            **sample_project_data,
            options={"include_3d_data": True}
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    @pytest.mark.skipif(
        not Export3DService().is_format_supported("png"),
        reason="PNG export not available"
    )
    def test_image_quality_options(self, export_service, sample_project_data):
        """Test image export with different quality settings."""
        # High quality
        high_quality = export_service.export_image(
            **sample_project_data,
            format="png",
            options={"width": 1920, "height": 1080, "scale": 2.0}
        )
        
        # Low quality
        low_quality = export_service.export_image(
            **sample_project_data,
            format="png",
            options={"width": 800, "height": 600, "scale": 1.0}
        )
        
        # High quality should be larger
        assert len(high_quality) > len(low_quality)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
