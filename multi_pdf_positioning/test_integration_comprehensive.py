"""
Comprehensive Integration Test Suite for Multi-PDF Positioning System

This test suite validates end-to-end workflows including:
- Complete workflow for single firma-seite combination
- Batch processing of multiple PDFs
- Backup and restore functionality
- Error handling and recovery
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from typing import List

# Import all modules
from multi_pdf_positioning.yml_parser import YMLParser
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
from multi_pdf_positioning.position_calculator import PositionCalculator
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.backup_manager import BackupManager
from multi_pdf_positioning.main_workflow import MainWorkflow
from multi_pdf_positioning.batch_processor import BatchProcessor


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_yml_content():
    """Create sample YML content."""
    return """Text: ERSTELLT FÜR:
Position: (48.0, 70.0, 220.0, 87.0)
Schriftart: Helvetica-Bold
Schriftgröße: 20.0
Farbe: 30920
----------------------------------------
Text: kunde_vorname_und_nachname
Position: (90.0, 87.0, 220.0, 105.0)
Schriftart: Helvetica-Bold
Schriftgröße: 14.0
Farbe: 3487029
----------------------------------------
Text: PHOTOVOLTAIK
Position: (48.0, 120.0, 250.0, 140.0)
Schriftart: Helvetica-Bold
Schriftgröße: 24.0
Farbe: 30920
----------------------------------------
"""


@pytest.fixture
def sample_yml_file(temp_dir, sample_yml_content):
    """Create a sample YML file."""
    yml_path = Path(temp_dir) / "test_seite1_f1.yml"
    yml_path.write_text(sample_yml_content, encoding='utf-8')
    return str(yml_path)


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

class TestEndToEndWorkflow:
    """Test complete end-to-end workflow for a single combination."""
    
    def test_complete_workflow_single_file(self, sample_yml_file, temp_dir):
        """Test complete workflow: parse -> calculate -> generate -> validate."""
        
        # Step 1: Parse YML file
        parser = YMLParser()
        elements = parser.parse_yml(sample_yml_file)
        
        assert len(elements) > 0, "Should parse elements"
        
        # Step 2: Create mock PDF analysis
        from multi_pdf_positioning.pdf_analyzer import PDFAnalysis, SafeZone
        
        pdf_analysis = PDFAnalysis(
            firma=1,
            seite=1,
            page_size={"width": 595, "height": 842},
            design_regions=[],
            visual_elements=[],
            safe_zones=[
                SafeZone(x1=50, y1=50, x2=545, y2=792)
            ],
            color_palette=["#007BFF", "#FFFFFF"]
        )
        
        # Step 3: Calculate new positions
        calculator = PositionCalculator()
        new_positions = calculator.calculate_positions(
            elements, pdf_analysis
        )
        
        assert len(new_positions) == len(elements), \
            "Should have position for each element"
        
        # Step 4: Validate positions
        is_valid, errors = calculator.validate_positions(new_positions)
        assert is_valid, f"Positions should be valid: {errors}"
        
        # Step 5: Generate new YML
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "output_seite1_f1.yml"
        
        content = generator.generate_yml(
            elements,
            new_positions,
            str(output_path),
            sample_yml_file
        )
        
        assert output_path.exists(), "Output file should be created"
        assert len(content) > 0, "Content should not be empty"
        
        # Step 6: Validate generated YML
        is_valid, errors = generator.validate_yml_output(
            str(output_path), elements
        )
        
        assert is_valid, f"Generated YML should be valid: {errors}"
        
        # Step 7: Parse generated file to verify
        parser2 = YMLParser()
        generated_elements = parser2.parse_yml(str(output_path))
        
        assert len(generated_elements) == len(elements), \
            "Should have same number of elements"
        
        # Verify attributes preserved (except position)
        for orig, gen in zip(elements, generated_elements):
            assert orig.text == gen.text, "Text should be preserved"
            assert orig.font == gen.font, "Font should be preserved"
            assert orig.font_size == gen.font_size, \
                "Font size should be preserved"
            assert orig.color == gen.color, "Color should be preserved"
    
    def test_workflow_with_collision_resolution(
        self, sample_yml_file, temp_dir
    ):
        """Test workflow handles collisions properly."""
        
        # Parse YML
        parser = YMLParser()
        elements = parser.parse_yml(sample_yml_file)
        
        # Create positions that will collide
        colliding_positions = [
            (50.0, 50.0, 150.0, 100.0),
            (100.0, 75.0, 200.0, 125.0),  # Overlaps with first
            (150.0, 100.0, 250.0, 150.0)
        ]
        
        # Check collisions are detected
        calculator = PositionCalculator()
        collisions = calculator.check_collisions(colliding_positions)
        
        assert len(collisions) > 0, "Should detect collisions"
        
        # Validation should fail
        is_valid, errors = calculator.validate_positions(colliding_positions)
        assert not is_valid, "Should detect collision errors"
        assert any("collision" in err.lower() for err in errors)
    
    def test_workflow_with_boundary_correction(
        self, sample_yml_file, temp_dir
    ):
        """Test workflow corrects out-of-bounds positions."""
        
        # Parse YML
        parser = YMLParser()
        elements = parser.parse_yml(sample_yml_file)
        
        # Create positions outside bounds
        out_of_bounds = [
            (-10.0, 50.0, 100.0, 100.0),  # x1 < 0
            (500.0, 50.0, 700.0, 100.0),  # x2 > 595
            (50.0, -10.0, 150.0, 100.0)   # y1 < 0
        ]
        
        # Correct bounds
        calculator = PositionCalculator()
        corrected = [calculator.ensure_bounds(pos) for pos in out_of_bounds]
        
        # Verify all corrected positions are within bounds
        for pos in corrected:
            x1, y1, x2, y2 = pos
            assert x1 >= 10, "x1 should be >= min_margin"
            assert y1 >= 10, "y1 should be >= min_margin"
            assert x2 <= 585, "x2 should be <= page_width - min_margin"
            assert y2 <= 832, "y2 should be <= page_height - min_margin"


# ============================================================================
# BATCH PROCESSING TESTS
# ============================================================================

class TestBatchProcessing:
    """Test batch processing of multiple files."""
    
    def test_batch_process_multiple_files(self, temp_dir, sample_yml_content):
        """Test processing multiple YML files in batch."""
        
        # Create multiple YML files
        yml_files = []
        for i in range(1, 4):
            yml_path = Path(temp_dir) / f"seite{i}_f1.yml"
            yml_path.write_text(sample_yml_content, encoding='utf-8')
            yml_files.append(str(yml_path))
        
        # Process all files
        results = {}
        for yml_file in yml_files:
            try:
                # Parse
                parser = YMLParser()
                elements = parser.parse_yml(yml_file)
                
                # Calculate positions (simple shift)
                new_positions = []
                for elem in elements:
                    x1, y1, x2, y2 = elem.position
                    new_positions.append((x1 + 10, y1 + 10, x2 + 10, y2 + 10))
                
                # Generate
                generator = YMLGenerator()
                output_path = yml_file.replace(".yml", "_output.yml")
                generator.generate_yml(
                    elements, new_positions, output_path, yml_file
                )
                
                # Validate
                is_valid, errors = generator.validate_yml_output(
                    output_path, elements
                )
                
                results[yml_file] = is_valid
                
            except Exception as e:
                results[yml_file] = False
                print(f"Error processing {yml_file}: {e}")
        
        # Check all succeeded
        assert all(results.values()), \
            f"All files should process successfully: {results}"
        assert len(results) == 3, "Should process all 3 files"
    
    def test_batch_process_with_errors(self, temp_dir):
        """Test batch processing handles errors gracefully."""
        
        # Create mix of valid and invalid files
        valid_yml = Path(temp_dir) / "valid.yml"
        valid_yml.write_text("""Text: Test
Position: (50.0, 50.0, 150.0, 100.0)
Schriftart: Helvetica
Schriftgröße: 12.0
Farbe: 0
----------------------------------------
""", encoding='utf-8')
        
        invalid_yml = Path(temp_dir) / "invalid.yml"
        invalid_yml.write_text("Invalid YML content", encoding='utf-8')
        
        # Process both files
        results = {}
        for yml_file in [str(valid_yml), str(invalid_yml)]:
            try:
                parser = YMLParser()
                elements = parser.parse_yml(yml_file)
                results[yml_file] = len(elements) > 0
            except Exception:
                results[yml_file] = False
        
        # Valid should succeed, invalid should fail
        assert results[str(valid_yml)], "Valid file should succeed"
        assert not results[str(invalid_yml)], "Invalid file should fail"


# ============================================================================
# BACKUP AND RESTORE TESTS
# ============================================================================

class TestBackupAndRestore:
    """Test backup and restore functionality."""
    
    def test_create_backup(self, temp_dir, sample_yml_content):
        """Test creating backup of YML files."""
        
        # Create original files
        yml_files = []
        for i in range(1, 3):
            yml_path = Path(temp_dir) / f"seite{i}_f1.yml"
            yml_path.write_text(sample_yml_content, encoding='utf-8')
            yml_files.append(yml_path)
        
        # Create backup
        backup_dir = Path(temp_dir) / "backups"
        backup_manager = BackupManager(yml_dir=temp_dir, backup_dir=backup_dir)
        backup_id = backup_manager.create_backup(yml_files)
        
        assert backup_id is not None, "Should create backup"
        
        # Verify backup exists
        backups = backup_manager.list_backups()
        assert len(backups) > 0, "Should have at least one backup"
        assert backup_id in [b["id"] for b in backups]
    
    def test_restore_backup(self, temp_dir, sample_yml_content):
        """Test restoring from backup."""
        
        # Create original file
        yml_path = Path(temp_dir) / "seite1_f1.yml"
        yml_path.write_text(sample_yml_content, encoding='utf-8')
        
        # Create backup
        backup_dir = Path(temp_dir) / "backups"
        backup_manager = BackupManager(yml_dir=temp_dir, backup_dir=backup_dir)
        backup_id = backup_manager.create_backup([yml_path])
        
        # Modify original file
        yml_path.write_text("Modified content", encoding='utf-8')
        assert yml_path.read_text() == "Modified content"
        
        # Restore from backup
        success = backup_manager.restore_backup(backup_id, [yml_path])
        
        assert success, "Restore should succeed"
        
        # Verify content restored
        restored_content = yml_path.read_text()
        assert "ERSTELLT FÜR:" in restored_content, \
            "Original content should be restored"
    
    def test_list_backups(self, temp_dir, sample_yml_content):
        """Test listing available backups."""
        
        # Create file and multiple backups
        yml_path = Path(temp_dir) / "seite1_f1.yml"
        yml_path.write_text(sample_yml_content, encoding='utf-8')
        
        backup_dir = Path(temp_dir) / "backups"
        backup_manager = BackupManager(yml_dir=temp_dir, backup_dir=backup_dir)
        
        # Create 3 backups
        backup_ids = []
        for i in range(3):
            backup_id = backup_manager.create_backup([yml_path])
            backup_ids.append(backup_id)
        
        # List backups
        backups = backup_manager.list_backups()
        
        assert len(backups) >= 3, "Should have at least 3 backups"
        
        # Verify all backup IDs are in list
        listed_ids = [b["id"] for b in backups]
        for backup_id in backup_ids:
            assert backup_id in listed_ids, \
                f"Backup {backup_id} should be in list"
    
    def test_validate_backup(self, temp_dir, sample_yml_content):
        """Test backup validation."""
        
        # Create file and backup
        yml_path = Path(temp_dir) / "seite1_f1.yml"
        yml_path.write_text(sample_yml_content, encoding='utf-8')
        
        backup_dir = Path(temp_dir) / "backups"
        backup_manager = BackupManager(yml_dir=temp_dir, backup_dir=backup_dir)
        backup_id = backup_manager.create_backup([yml_path])
        
        # Validate backup
        is_valid = backup_manager.validate_backup(backup_id)
        
        assert is_valid, "Backup should be valid"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_handle_missing_yml_file(self):
        """Test handling of missing YML file."""
        parser = YMLParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_yml("nonexistent_file.yml")
    
    def test_handle_invalid_yml_format(self, temp_dir):
        """Test handling of invalid YML format."""
        # Create invalid YML file
        invalid_yml = Path(temp_dir) / "invalid.yml"
        invalid_yml.write_text("This is not valid YML format", encoding='utf-8')
        
        parser = YMLParser()
        elements = parser.parse_yml(str(invalid_yml))
        
        # Should return empty list or handle gracefully
        assert isinstance(elements, list), "Should return list"
    
    def test_handle_position_mismatch(self, temp_dir, sample_yml_content):
        """Test handling of element/position count mismatch."""
        # Create YML file
        yml_path = Path(temp_dir) / "test.yml"
        yml_path.write_text(sample_yml_content, encoding='utf-8')
        
        # Parse elements
        parser = YMLParser()
        elements = parser.parse_yml(str(yml_path))
        
        # Try to generate with wrong number of positions
        generator = YMLGenerator()
        wrong_positions = [(50.0, 50.0, 150.0, 100.0)]  # Only 1 position
        
        output_path = Path(temp_dir) / "output.yml"
        
        with pytest.raises(ValueError, match="Mismatch"):
            generator.generate_yml(
                elements, wrong_positions, str(output_path)
            )
    
    def test_handle_invalid_position_bounds(self, temp_dir):
        """Test handling of positions outside valid bounds."""
        from multi_pdf_positioning.yml_parser import YMLElement
        
        elements = [
            YMLElement(
                text="Test",
                position=(50.0, 50.0, 150.0, 100.0),
                font="Helvetica",
                font_size=12.0,
                color=0,
                index=0
            )
        ]
        
        # Create invalid positions
        invalid_positions = [(600.0, 50.0, 700.0, 100.0)]  # x > 595
        
        # Generate YML (should succeed)
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "test.yml"
        
        generator.generate_yml(elements, invalid_positions, str(output_path))
        
        # But validation should fail
        is_valid, errors = generator.validate_yml_output(
            str(output_path), elements
        )
        
        assert not is_valid, "Should detect invalid bounds"
        assert len(errors) > 0, "Should have error messages"
    
    def test_recover_from_backup_on_error(self, temp_dir, sample_yml_content):
        """Test recovery from backup when generation fails."""
        
        # Create original file
        yml_path = Path(temp_dir) / "seite1_f1.yml"
        yml_path.write_text(sample_yml_content, encoding='utf-8')
        
        # Create backup
        backup_dir = Path(temp_dir) / "backups"
        backup_manager = BackupManager(yml_dir=temp_dir, backup_dir=backup_dir)
        backup_id = backup_manager.create_backup([yml_path])
        
        # Simulate error by corrupting file
        yml_path.write_text("Corrupted content", encoding='utf-8')
        
        # Restore from backup
        success = backup_manager.restore_backup(backup_id, [yml_path])
        
        assert success, "Should restore from backup"
        
        # Verify restoration
        content = yml_path.read_text()
        assert "ERSTELLT FÜR:" in content, "Should restore original content"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance with larger datasets."""
    
    def test_process_many_elements(self, temp_dir):
        """Test processing file with many elements."""
        
        # Create YML with 50 elements
        yml_content = ""
        for i in range(50):
            yml_content += f"""Text: Element {i}
Position: ({50 + i*10}.0, {50 + i*5}.0, {150 + i*10}.0, {100 + i*5}.0)
Schriftart: Helvetica
Schriftgröße: 12.0
Farbe: 0
----------------------------------------
"""
        
        yml_path = Path(temp_dir) / "large.yml"
        yml_path.write_text(yml_content, encoding='utf-8')
        
        # Parse
        parser = YMLParser()
        elements = parser.parse_yml(str(yml_path))
        
        assert len(elements) == 50, "Should parse all 50 elements"
        
        # Calculate positions
        from multi_pdf_positioning.pdf_analyzer import PDFAnalysis, SafeZone
        
        pdf_analysis = PDFAnalysis(
            firma=1, seite=1,
            page_size={"width": 595, "height": 842},
            design_regions=[], visual_elements=[],
            safe_zones=[SafeZone(x1=50, y1=50, x2=545, y2=792)],
            color_palette=[]
        )
        
        calculator = PositionCalculator()
        new_positions = calculator.calculate_positions(elements, pdf_analysis)
        
        assert len(new_positions) == 50, "Should calculate all positions"
        
        # Generate
        generator = YMLGenerator()
        output_path = Path(temp_dir) / "large_output.yml"
        
        content = generator.generate_yml(
            elements, new_positions, str(output_path)
        )
        
        assert len(content) > 0, "Should generate content"
        assert output_path.exists(), "Should create output file"


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
