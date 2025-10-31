"""
Test suite for coding tools
Tests file system operations and project structure generation
"""
from agent.tools.coding_tools import (
    AGENT_WORKSPACE,
    generate_project_structure,
    list_files,
    read_file,
    write_file,
)
import os
import shutil
import sys

import pytest

# Add Agent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestFileOperations:
    """Test basic file operations."""

    def setup_method(self):
        """Clean workspace before each test."""
        if os.path.exists(AGENT_WORKSPACE):
            shutil.rmtree(AGENT_WORKSPACE)
        os.makedirs(AGENT_WORKSPACE)

    def teardown_method(self):
        """Clean workspace after each test."""
        if os.path.exists(AGENT_WORKSPACE):
            shutil.rmtree(AGENT_WORKSPACE)

    def test_write_file_basic(self):
        """Test basic file writing."""
        result = write_file.invoke(
            {"path": "test.txt", "content": "Hello World"})
        assert "erfolgreich" in result
        assert os.path.exists(os.path.join(AGENT_WORKSPACE, "test.txt"))

    def test_write_file_with_subdirectory(self):
        """Test writing file in subdirectory."""
        result = write_file.invoke({
            "path": "subdir/test.txt",
            "content": "Hello World"
        })
        assert "erfolgreich" in result
        assert os.path.exists(
            os.path.join(AGENT_WORKSPACE, "subdir", "test.txt")
        )

    def test_write_file_directory_traversal_prevention(self):
        """Test that directory traversal is prevented."""
        result = write_file.invoke({
            "path": "../../../etc/passwd",
            "content": "malicious"
        })
        assert "Fehler" in result
        assert "nicht erlaubt" in result.lower()

    def test_write_file_absolute_path_prevention(self):
        """Test that absolute paths are prevented."""
        result = write_file.invoke({
            "path": "/etc/passwd",
            "content": "malicious"
        })
        assert "Fehler" in result

    def test_read_file_basic(self):
        """Test basic file reading."""
        # First write a file
        write_file.invoke({"path": "test.txt", "content": "Hello World"})

        # Then read it
        result = read_file.invoke({"path": "test.txt"})
        assert result == "Hello World"

    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        result = read_file.invoke({"path": "nonexistent.txt"})
        assert "Fehler" in result
        assert "nicht gefunden" in result

    def test_read_file_directory_traversal_prevention(self):
        """Test that directory traversal is prevented in read."""
        result = read_file.invoke({"path": "../../../etc/passwd"})
        assert "Fehler" in result
        assert "nicht erlaubt" in result.lower()

    def test_list_files_empty_directory(self):
        """Test listing empty directory."""
        result = list_files.invoke({"path": "."})
        assert "leer" in result.lower()

    def test_list_files_with_content(self):
        """Test listing directory with files."""
        # Create some files
        write_file.invoke({"path": "file1.txt", "content": "content1"})
        write_file.invoke({"path": "file2.txt", "content": "content2"})
        os.makedirs(os.path.join(AGENT_WORKSPACE, "subdir"))

        # List files
        result = list_files.invoke({"path": "."})
        assert "[FILE]" in result
        assert "[DIR]" in result
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result

    def test_list_files_directory_traversal_prevention(self):
        """Test that directory traversal is prevented in list."""
        result = list_files.invoke({"path": "../../.."})
        assert "Fehler" in result
        assert "nicht erlaubt" in result.lower()


class TestProjectStructureGeneration:
    """Test project structure generation."""

    def setup_method(self):
        """Clean workspace before each test."""
        if os.path.exists(AGENT_WORKSPACE):
            shutil.rmtree(AGENT_WORKSPACE)
        os.makedirs(AGENT_WORKSPACE)

    def teardown_method(self):
        """Clean workspace after each test."""
        if os.path.exists(AGENT_WORKSPACE):
            shutil.rmtree(AGENT_WORKSPACE)

    def test_generate_flask_api_project(self):
        """Test generating Flask API project."""
        result = generate_project_structure.invoke({
            "project_name": "TestFlaskAPI",
            "project_type": "flask_api"
        })

        assert "erfolgreich" in result
        assert "Flask REST API" in result

        # Check directory structure
        project_path = os.path.join(AGENT_WORKSPACE, "testflaskapi")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "app"))
        assert os.path.exists(os.path.join(project_path, "tests"))
        assert os.path.exists(os.path.join(project_path, "requirements.txt"))
        assert os.path.exists(os.path.join(project_path, "README.md"))

    def test_generate_streamlit_app_project(self):
        """Test generating Streamlit app project."""
        result = generate_project_structure.invoke({
            "project_name": "TestStreamlitApp",
            "project_type": "streamlit_app"
        })

        assert "erfolgreich" in result
        assert "Streamlit" in result

        # Check directory structure
        project_path = os.path.join(AGENT_WORKSPACE, "teststreamlitapp")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "app.py"))
        assert os.path.exists(os.path.join(project_path, "pages"))
        assert os.path.exists(os.path.join(project_path, "components"))

    def test_generate_fastapi_service_project(self):
        """Test generating FastAPI service project."""
        result = generate_project_structure.invoke({
            "project_name": "TestFastAPI",
            "project_type": "fastapi_service"
        })

        assert "erfolgreich" in result
        assert "FastAPI" in result

        # Check directory structure
        project_path = os.path.join(AGENT_WORKSPACE, "testfastapi")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "app"))
        assert os.path.exists(os.path.join(project_path, "app", "main.py"))

    def test_generate_python_package_project(self):
        """Test generating Python package project."""
        result = generate_project_structure.invoke({
            "project_name": "TestPackage",
            "project_type": "python_package"
        })

        assert "erfolgreich" in result

        # Check directory structure
        project_path = os.path.join(AGENT_WORKSPACE, "testpackage")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "src"))
        assert os.path.exists(os.path.join(project_path, "tests"))
        assert os.path.exists(os.path.join(project_path, "setup.py"))
        assert os.path.exists(os.path.join(project_path, "pyproject.toml"))

    def test_generate_data_analysis_project(self):
        """Test generating data analysis project."""
        result = generate_project_structure.invoke({
            "project_name": "TestDataAnalysis",
            "project_type": "data_analysis"
        })

        assert "erfolgreich" in result

        # Check directory structure
        project_path = os.path.join(AGENT_WORKSPACE, "testdataanalysis")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "data"))
        assert os.path.exists(os.path.join(project_path, "notebooks"))
        assert os.path.exists(os.path.join(project_path, "src"))

    def test_generate_project_invalid_type(self):
        """Test generating project with invalid type."""
        result = generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "invalid_type"
        })

        assert "Fehler" in result
        assert "Unbekannter Projekttyp" in result

    def test_generate_project_already_exists(self):
        """Test generating project that already exists."""
        # Create project first time
        generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "flask_api"
        })

        # Try to create again
        result = generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "flask_api"
        })

        assert "Fehler" in result
        assert "existiert bereits" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
