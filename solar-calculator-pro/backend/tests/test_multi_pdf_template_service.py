"""
Tests for Multi-PDF Template & Koordinaten System Service

Requirements: 1.3, 6.1, 7.3
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

from services.multi_pdf_template_service import (
    MultiPDFTemplateService,
    TemplateInfo,
    CoordinateInfo
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    temp_dir = tempfile.mkdtemp()
    template_dir = Path(temp_dir) / "pdf_templates_static" / "multi"
    coord_dir = Path(temp_dir) / "coords_multi"
    
    template_dir.mkdir(parents=True, exist_ok=True)
    coord_dir.mkdir(parents=True, exist_ok=True)
    
    yield template_dir, coord_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def service(temp_dirs):
    """Create service instance with temporary directories"""
    template_dir, coord_dir = temp_dirs
    return MultiPDFTemplateService(
        template_base_dir=str(template_dir),
        coordinate_base_dir=str(coord_dir)
    )


@pytest.fixture
def sample_templates(temp_dirs):
    """Create sample template files"""
    template_dir, _ = temp_dirs
    
    # Create templates for company 1 (pages 1-8)
    for page in range(1, 9):
        template_path = template_dir / f"multi_nt_{page:02d}_f1.pdf"
        template_path.write_bytes(b"%PDF-1.4\nSample PDF content")
    
    # Create templates for company 2 (pages 1-5 only)
    for page in range(1, 6):
        template_path = template_dir / f"multi_nt_{page:02d}_f2.pdf"
        template_path.write_bytes(b"%PDF-1.4\nSample PDF content")
    
    return template_dir


@pytest.fixture
def sample_coordinates(temp_dirs):
    """Create sample coordinate files"""
    _, coord_dir = temp_dirs
    
    # Create coordinates for company 1 (pages 1-8)
    for page in range(1, 9):
        coord_path = coord_dir / f"seite{page}_f1.yml"
        coord_data = {
            "title": {"x": 100, "y": 200, "font_size": 24},
            "subtitle": {"x": 100, "y": 250, "font_size": 16}
        }
        with open(coord_path, 'w') as f:
            yaml.dump(coord_data, f)
    
    # Create coordinates for company 2 (pages 1-5 only)
    for page in range(1, 6):
        coord_path = coord_dir / f"seite{page}_f2.yml"
        coord_data = {
            "title": {"x": 120, "y": 220, "font_size": 22},
            "subtitle": {"x": 120, "y": 270, "font_size": 14}
        }
        with open(coord_path, 'w') as f:
            yaml.dump(coord_data, f)
    
    return coord_dir


class TestMultiPDFTemplateService:
    """Test suite for MultiPDFTemplateService"""
    
    def test_initialization(self, service):
        """Test service initialization"""
        assert service.template_base_dir.exists()
        assert service.coordinate_base_dir.exists()
        assert service.template_pattern == "multi_nt_{page:02d}_f{company}.pdf"
        assert service.coordinate_pattern == "seite{page}_f{company}.yml"
    
    def test_get_template_path(self, service):
        """Test template path generation"""
        path = service.get_template_path(company_id=1, page_number=3)
        assert path.name == "multi_nt_03_f1.pdf"
        
        path = service.get_template_path(company_id=5, page_number=8)
        assert path.name == "multi_nt_08_f5.pdf"
    
    def test_get_coordinate_path(self, service):
        """Test coordinate path generation"""
        path = service.get_coordinate_path(company_id=1, page_number=3)
        assert path.name == "seite3_f1.yml"
        
        path = service.get_coordinate_path(company_id=5, page_number=8)
        assert path.name == "seite8_f5.yml"
    
    def test_load_template_success(self, service, sample_templates):
        """Test successful template loading"""
        content = service.load_template(company_id=1, page_number=1)
        assert content is not None
        assert b"%PDF-1.4" in content
    
    def test_load_template_not_found(self, service, sample_templates):
        """Test template loading when file doesn't exist"""
        content = service.load_template(company_id=99, page_number=1)
        assert content is None
    
    def test_load_coordinates_success(self, service, sample_coordinates):
        """Test successful coordinate loading"""
        coords = service.load_coordinates(company_id=1, page_number=1)
        assert coords is not None
        assert "title" in coords
        assert coords["title"]["x"] == 100
        assert coords["title"]["y"] == 200
    
    def test_load_coordinates_not_found(self, service, sample_coordinates):
        """Test coordinate loading when file doesn't exist"""
        coords = service.load_coordinates(company_id=99, page_number=1)
        assert coords is None
    
    def test_get_template_info(self, service, sample_templates):
        """Test getting template information"""
        info = service.get_template_info(company_id=1, page_number=1)
        assert isinstance(info, TemplateInfo)
        assert info.company_id == 1
        assert info.page_number == 1
        assert info.exists is True
        assert info.file_size is not None
        assert info.file_size > 0
    
    def test_get_template_info_not_found(self, service, sample_templates):
        """Test getting template info for non-existent file"""
        info = service.get_template_info(company_id=99, page_number=1)
        assert isinstance(info, TemplateInfo)
        assert info.exists is False
        assert info.file_size is None
    
    def test_get_coordinate_info(self, service, sample_coordinates):
        """Test getting coordinate information"""
        info = service.get_coordinate_info(company_id=1, page_number=1)
        assert isinstance(info, CoordinateInfo)
        assert info.company_id == 1
        assert info.page_number == 1
        assert info.exists is True
        assert info.coordinates is not None
    
    def test_get_coordinate_info_not_found(self, service, sample_coordinates):
        """Test getting coordinate info for non-existent file"""
        info = service.get_coordinate_info(company_id=99, page_number=1)
        assert isinstance(info, CoordinateInfo)
        assert info.exists is False
        assert info.coordinates is None
    
    def test_get_all_templates_for_company(self, service, sample_templates):
        """Test getting all templates for a company"""
        templates = service.get_all_templates_for_company(company_id=1, pages=8)
        assert len(templates) == 8
        assert all(isinstance(t, TemplateInfo) for t in templates)
        assert all(t.exists for t in templates)
    
    def test_get_all_coordinates_for_company(self, service, sample_coordinates):
        """Test getting all coordinates for a company"""
        coordinates = service.get_all_coordinates_for_company(company_id=1, pages=8)
        assert len(coordinates) == 8
        assert all(isinstance(c, CoordinateInfo) for c in coordinates)
        assert all(c.exists for c in coordinates)
    
    def test_discover_companies(self, service, sample_templates):
        """Test company discovery"""
        companies = service.discover_companies()
        assert len(companies) == 2
        assert 1 in companies
        assert 2 in companies
        assert companies == [1, 2]  # Should be sorted
    
    def test_validate_company_templates_success(self, service, sample_templates):
        """Test template validation for complete company"""
        is_valid, missing = service.validate_company_templates(company_id=1, pages=8)
        assert is_valid is True
        assert len(missing) == 0
    
    def test_validate_company_templates_incomplete(self, service, sample_templates):
        """Test template validation for incomplete company"""
        is_valid, missing = service.validate_company_templates(company_id=2, pages=8)
        assert is_valid is False
        assert len(missing) == 3  # Pages 6, 7, 8 are missing
    
    def test_validate_company_coordinates_success(self, service, sample_coordinates):
        """Test coordinate validation for complete company"""
        is_valid, missing = service.validate_company_coordinates(company_id=1, pages=8)
        assert is_valid is True
        assert len(missing) == 0
    
    def test_validate_company_coordinates_incomplete(self, service, sample_coordinates):
        """Test coordinate validation for incomplete company"""
        is_valid, missing = service.validate_company_coordinates(company_id=2, pages=8)
        assert is_valid is False
        assert len(missing) == 3  # Pages 6, 7, 8 are missing
    
    def test_batch_load_templates(self, service, sample_templates):
        """Test batch loading of templates"""
        result = service.batch_load_templates(company_ids=[1, 2], pages=5)
        
        assert len(result) == 2
        assert 1 in result
        assert 2 in result
        
        # Company 1 should have all 5 pages
        assert len(result[1]) == 5
        assert all(result[1][page] is not None for page in range(1, 6))
        
        # Company 2 should have all 5 pages
        assert len(result[2]) == 5
        assert all(result[2][page] is not None for page in range(1, 6))
    
    def test_batch_load_coordinates(self, service, sample_coordinates):
        """Test batch loading of coordinates"""
        result = service.batch_load_coordinates(company_ids=[1, 2], pages=5)
        
        assert len(result) == 2
        assert 1 in result
        assert 2 in result
        
        # Company 1 should have all 5 pages
        assert len(result[1]) == 5
        assert all(result[1][page] is not None for page in range(1, 6))
        
        # Company 2 should have all 5 pages
        assert len(result[2]) == 5
        assert all(result[2][page] is not None for page in range(1, 6))
    
    def test_get_company_summary(self, service, sample_templates, sample_coordinates):
        """Test getting company summary"""
        summary = service.get_company_summary(company_id=1)
        
        assert summary["company_id"] == 1
        assert summary["templates"]["total"] == 8
        assert summary["templates"]["existing"] == 8
        assert summary["templates"]["valid"] is True
        assert summary["coordinates"]["total"] == 8
        assert summary["coordinates"]["existing"] == 8
        assert summary["coordinates"]["valid"] is True
        assert summary["ready_for_generation"] is True
    
    def test_get_company_summary_incomplete(self, service, sample_templates, sample_coordinates):
        """Test getting summary for incomplete company"""
        summary = service.get_company_summary(company_id=2)
        
        assert summary["company_id"] == 2
        assert summary["templates"]["total"] == 8
        assert summary["templates"]["existing"] == 5
        assert summary["templates"]["valid"] is False
        assert summary["coordinates"]["total"] == 8
        assert summary["coordinates"]["existing"] == 5
        assert summary["coordinates"]["valid"] is False
        assert summary["ready_for_generation"] is False
    
    def test_get_all_companies_summary(self, service, sample_templates, sample_coordinates):
        """Test getting summary for all companies"""
        summary = service.get_all_companies_summary()
        
        assert summary["total_companies"] == 2
        assert summary["companies_ready"] == 1  # Only company 1 is complete
        assert summary["companies_with_issues"] == 1  # Company 2 is incomplete
        assert summary["company_ids"] == [1, 2]
        assert 1 in summary["details"]
        assert 2 in summary["details"]
    
    def test_empty_directories(self, service):
        """Test behavior with empty directories"""
        companies = service.discover_companies()
        assert len(companies) == 0
        
        summary = service.get_all_companies_summary()
        assert summary["total_companies"] == 0
        assert summary["companies_ready"] == 0
    
    def test_invalid_filename_format(self, temp_dirs, service):
        """Test handling of invalid filename formats"""
        template_dir, _ = temp_dirs
        
        # Create file with invalid format
        invalid_file = template_dir / "invalid_format.pdf"
        invalid_file.write_bytes(b"%PDF-1.4\nInvalid")
        
        companies = service.discover_companies()
        assert len(companies) == 0  # Should not discover invalid files
    
    def test_coordinate_parsing_error(self, temp_dirs, service):
        """Test handling of coordinate parsing errors"""
        _, coord_dir = temp_dirs
        
        # Create invalid YAML file
        invalid_coord = coord_dir / "seite1_f1.yml"
        invalid_coord.write_text("invalid: yaml: content: [")
        
        coords = service.load_coordinates(company_id=1, page_number=1)
        assert coords is None  # Should return None on parsing error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
