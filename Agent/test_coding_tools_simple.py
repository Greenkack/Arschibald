"""
Simple test for coding tools - direct import without package initialization
"""
from agent.tools import coding_tools
import os
import shutil
import sys

# Add paths
agent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, agent_dir)

# Direct import from module

AGENT_WORKSPACE = coding_tools.AGENT_WORKSPACE


def setup_workspace():
    """Clean workspace before tests."""
    if os.path.exists(AGENT_WORKSPACE):
        shutil.rmtree(AGENT_WORKSPACE)
    os.makedirs(AGENT_WORKSPACE)


def teardown_workspace():
    """Clean workspace after tests."""
    if os.path.exists(AGENT_WORKSPACE):
        shutil.rmtree(AGENT_WORKSPACE)


def test_write_file_basic():
    """Test basic file writing."""
    setup_workspace()
    try:
        result = coding_tools.write_file.invoke({
            "path": "test.txt",
            "content": "Hello World"
        })
        assert "erfolgreich" in result
        assert os.path.exists(os.path.join(AGENT_WORKSPACE, "test.txt"))
        print("✓ test_write_file_basic passed")
    finally:
        teardown_workspace()


def test_write_file_directory_traversal():
    """Test directory traversal prevention."""
    setup_workspace()
    try:
        result = coding_tools.write_file.invoke({
            "path": "../../../etc/passwd",
            "content": "malicious"
        })
        assert "Fehler" in result
        assert "nicht erlaubt" in result.lower()
        print("✓ test_write_file_directory_traversal passed")
    finally:
        teardown_workspace()


def test_read_file_basic():
    """Test basic file reading."""
    setup_workspace()
    try:
        # Write file first
        coding_tools.write_file.invoke({
            "path": "test.txt",
            "content": "Hello World"
        })

        # Read it back
        result = coding_tools.read_file.invoke({"path": "test.txt"})
        assert result == "Hello World"
        print("✓ test_read_file_basic passed")
    finally:
        teardown_workspace()


def test_read_file_not_found():
    """Test reading non-existent file."""
    setup_workspace()
    try:
        result = coding_tools.read_file.invoke({"path": "nonexistent.txt"})
        assert "Fehler" in result
        assert "nicht gefunden" in result
        print("✓ test_read_file_not_found passed")
    finally:
        teardown_workspace()


def test_list_files_empty():
    """Test listing empty directory."""
    setup_workspace()
    try:
        result = coding_tools.list_files.invoke({"path": "."})
        assert "leer" in result.lower()
        print("✓ test_list_files_empty passed")
    finally:
        teardown_workspace()


def test_list_files_with_content():
    """Test listing directory with files."""
    setup_workspace()
    try:
        # Create files
        coding_tools.write_file.invoke({
            "path": "file1.txt",
            "content": "content1"
        })
        coding_tools.write_file.invoke({
            "path": "file2.txt",
            "content": "content2"
        })
        os.makedirs(os.path.join(AGENT_WORKSPACE, "subdir"))

        # List files
        result = coding_tools.list_files.invoke({"path": "."})
        assert "[FILE]" in result
        assert "[DIR]" in result
        assert "file1.txt" in result
        assert "file2.txt" in result
        print("✓ test_list_files_with_content passed")
    finally:
        teardown_workspace()


def test_generate_flask_api_project():
    """Test generating Flask API project."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "TestFlaskAPI",
            "project_type": "flask_api"
        })

        assert "erfolgreich" in result
        assert "Flask REST API" in result

        # Check structure
        project_path = os.path.join(AGENT_WORKSPACE, "testflaskapi")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "app"))
        assert os.path.exists(os.path.join(project_path, "tests"))
        assert os.path.exists(os.path.join(project_path, "requirements.txt"))
        assert os.path.exists(os.path.join(project_path, "README.md"))
        print("✓ test_generate_flask_api_project passed")
    finally:
        teardown_workspace()


def test_generate_streamlit_app_project():
    """Test generating Streamlit app project."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "TestStreamlitApp",
            "project_type": "streamlit_app"
        })

        assert "erfolgreich" in result

        # Check structure
        project_path = os.path.join(AGENT_WORKSPACE, "teststreamlitapp")
        assert os.path.exists(project_path)
        assert os.path.exists(os.path.join(project_path, "app.py"))
        assert os.path.exists(os.path.join(project_path, "pages"))
        print("✓ test_generate_streamlit_app_project passed")
    finally:
        teardown_workspace()


def test_generate_project_invalid_type():
    """Test generating project with invalid type."""
    setup_workspace()
    try:
        result = coding_tools.generate_project_structure.invoke({
            "project_name": "TestProject",
            "project_type": "invalid_type"
        })

        assert "Fehler" in result
        assert "Unbekannter Projekttyp" in result
        print("✓ test_generate_project_invalid_type passed")
    finally:
        teardown_workspace()


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Coding Tools Tests")
    print("=" * 60 + "\n")

    tests = [
        test_write_file_basic,
        test_write_file_directory_traversal,
        test_read_file_basic,
        test_read_file_not_found,
        test_list_files_empty,
        test_list_files_with_content,
        test_generate_flask_api_project,
        test_generate_streamlit_app_project,
        test_generate_project_invalid_type,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
